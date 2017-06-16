from paramiko import SSHClient
from paramiko import AutoAddPolicy
from  scp import SCPClient
import os
import configparser
from datetime import datetime

class transferFilesSCP(object):
    __version__ = "0.0.1"
    __name__ ="__fileTransfer__"

    def __init__(self):
        self.getConfig()
        self.openConnection()

    def getConfig(self):
        path = os.getcwd()
        if os.path.split(path)[1] != "BoP":
            path = os.path.split(path)[0]
            if os.path.split(path)[1] != "BoP":
                msg = "Error at {0}".format(path)
                raise ValueError(msg)
        self.path = path
        self.config = configparser.ConfigParser()
        filepath = "/repos/config/configNowcasting.ini"
        self.config.read(filepath)

        ## -- Server settings -- ##
        self.user = self.config["webpage"].get("user")
        self.host = self.config["webpage"].get("host")
        self.passwd = self.config["webpage"].get("password")

    def openConnection(self):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(hostname=self.host, username=self.user, password=self.passwd)

    def transfer(self, filepath:str, outputPath:str=""):
        with SCPClient(self.ssh.get_transport()) as scp:
            scp.put(files=filepath, remote_path='/var/www/html/nowcast/public_html/' + outputPath)

    def getFiles(self, remotePath:str):
        localPath = self.path + "\\html\\"
        with SCPClient(self.ssh.get_transport()) as scp:
            scp.get(local_path=localPath, remote_path=remotePath)

    def closeConnection(self):
        self.ssh.close()

    def cleanExternalFolder(self, timestamp:datetime = datetime.now(), path:str = "/var/www/html/nowcast/public_html/img/kloflow/", universe:str="EM"):
        command = "ls {0:s}".format(path)
        (stdin, stdout, stderr) = self.ssh.exec_command(command)

        store = []
        if universe.lower() == "etf":

            for line in stdout.readlines():
                tmp = line.split("_")[1].split(".")[0]
                if (tmp != "{0:%Y-%m-%d-%H-%M}".format(timestamp)):
                    store.append(line.strip("\n"))
        else:
            for line in stdout.readlines():
                world = line.split("_")[1]
                tmp = line.split("_")[-1].split(".")[0]
                if (tmp != "{0:%Y-%m-%d-%H-%M}".format(timestamp)) & (world == universe):
                    store.append(line.strip("\n"))

        for ii in store:
            command = "rm {0:s}{1:s}".format(path, ii)
            self.ssh.exec_command(command)

    def __del__(self):
        self.closeConnection()

if __name__ == "__main__":
    print(os.getcwd())
    scp = transferFilesSCP()
    scp.getFiles(remotePath="/var/www/html/nowcast/public_html/index.html")
