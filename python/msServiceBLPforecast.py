import os
import sys
import datetime
import logging
import socket
import time
import win32serviceutil
import win32service
import win32event
import win32api
import servicemanager
import traceback
import win32com.client
import getpass
from email.message import EmailMessage
from email.headerregistry import Address
import smtplib
import configparser

#from msp_Logging import mspLog
name = "msBloombergForecastService"
dev = True
now = datetime.datetime.now()
FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
if dev:
    log_filename = '/repos/Nowcast/logs/{0:%Y-%m-%d}_{1:s}_DEV_logfile_{2:s}.log'.format(now, name, socket.gethostname())
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)
else:
    log_filename = '/repos/Nowcast/logs/{0:%Y-%m-%d}_{1:s}_UAT_logfile_{2:s}.log'.format(now, name, socket.gethostname())
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)



## -- Own Modules -- ##
from createBloombergForecastDB import createBloombergForecastDB

class msServiceBLPforecast(win32serviceutil.ServiceFramework):
    """A service that polls the database checking when the next release date is"""
    _svc_name_ = "msServiceBLPforecast"
    _svc_display_name_ = "Macrosynergy Forecasts Bloomberg Service"
    _svc_description_ = "This service downloads the Macro Forecasts from Bloomberg."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        try:
            self.config = configparser.ConfigParser()
            self.config.read('/repos/Nowcast/config/configNowcasting.ini')
        except Exception as e:
            servicemanager.LogErrorMsg(traceback.format_exc())
            logging.info("Error in init: %s", e)
            raise

    def LaunchModelScript(self):
        logging.info("Initiate the Model {0}".format(datetime.datetime.now()))

        ## -- The KloFlow Model -- ##
        try:
            self.forecasts.fcstDownloadData()
        except:
            logging.info("Error running the Bloomberg data program for macro forecasts: {0}".format(traceback.format_exc()))
            self.sendErrorMail(str(traceback.format_exc()))
            servicemanager.LogErrorMsg(traceback.format_exc())
            raise

    def sendErrorMail(self, message):
        server = smtplib.SMTP(self.config['EMAIL']['email_server'])
        server.starttls()
        sender = self.config['EMAIL']['email_sender']
        receiver = self.config['EMAIL']['email_error_recv']
        msg = EmailMessage()
        msg['Subject'] = "Nowcasting Update: Bloomberg Macro Forecasts data"
        msg['From'] = sender
        msg['To'] = receiver

        txt  = "<p> There has been an exception raised in the Forecasts Bloomberg data service. Please investigate</p>"
        txt += '<p>' +  message + '</p>'
        msg.add_alternative(txt, subtype='html')

        server.send_message(msg)
        server.quit()

    def SvcStop(self):
        logging.info("msBLPforecastService stopped")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.timeout = 3 * 1000 * 60 * 60 # 3 hours wait time
        self.weekendTimeoutExtra = 0
        logging.info("Starting SvcDoRun with timeout: {0} seconds".format(self.timeout*0.001))
        logging.info("msBloombergForecastService start modules")
        try:
            logging.info("Run Bloomberg Forecasts Model")
            self.forecasts = createBloombergForecastDB(dev=True)
            self.LaunchModelScript()
        except:
            self.sendErrorMail(str(traceback.format_exc()))
            logging.info("Connection failed with: {0}".format(traceback.format_exc()))
            servicemanager.LogErrorMsg(traceback.format_exc())
            raise

        logging.info("msBloombergForecastService initiated: run SvcDoRun")
        while 1:
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout+self.weekendTimeoutExtra)
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("msBloombergForecastService Stopped")
                break
            else:
                try:
                    servicemanager.LogInfoMsg("msBloombergForecastService: Getting started")
                    logging.info("Opening Forecasts Bloomberg within Service: ")
                    now = datetime.datetime.now()

                    if (now.isoweekday() <= 5):
                        logging.info("Update dataset: Bloomberg Forecasts")
                        self.LaunchModelScript()
                        self.weekendTimeoutExtra = 0
                    else:
                        logging.info("Stop for the Weekend at {0:%A %Y-%m-%d %H:%M}".format(now))
                        self.weekendTimeoutExtra = 24 * 1000 * 60 * 60 # 24 hours

                    logging.info("Next check will be: {0:%Y-%m-%d %H:%M}".format(now + datetime.timedelta(seconds = ((self.timeout +self.weekendTimeoutExtra) * 0.001))))
                except:
                    self.sendErrorMail(str(traceback.format_exc()))
                    logging.info("Connection failed with: {0}".format(traceback.format_exc()))
                    servicemanager.LogErrorMsg(traceback.format_exc())
                    pass

def ctrlHandler(ctrlType):
   return True

if __name__ == '__main__':
    win32api.SetConsoleCtrlHandler(ctrlHandler, True)
    win32serviceutil.HandleCommandLine(msServiceBLPforecast)
