import win32serviceutil
import win32service
import win32event
import win32api
import servicemanager
import datetime
import logging
import traceback
import win32com.client
import pywintypes
import os
import subprocess
import shutil
from email.message import EmailMessage
import smtplib
import pandas as pd
import configparser
from pytz import timezone

## Own Modules
from msDbaseInterface import msMBDbInterface
from mainMixed import nowcastModel

class msServiceMBDb(win32serviceutil.ServiceFramework):
    """A service that polls the database checking when the next release date is"""
    _svc_name_ = "msServiceMBDb"
    _svc_display_name_ = "Macrosynergy Macrobond DB Service"
    _svc_description_ = "This service queries the Macrosynergy economic indicator database, checks if there are any releases due"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.tz = timezone("Europe/London")
        try:
            self.config = configparser.ConfigParser()
            self.config.read('/repos/Nowcast/config/configNowcasting.ini')
        except Exception as e:
            servicemanager.LogErrorMsg(traceback.format_exc())
            logging.info("Error in init: %s", e)
            raise

    def SvcStop(self):
        #  logging.info("Stopping....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def checkConfig(self):
        option_names = [ 'db_user', 'db_password', 'db_host', 'db_name', 'file_output', 'email_sender', 'email_receiver', 'email_server']
        sections = self.config.sections()
        for name in option_names:
            for sect in sections:
                try:
                    value = self.config.get(sect, name)
                except configparser.ConfigParser.NoOptionError as err:
                    raise err

    def indicatorChange(self, mb_db_conn, updated_indicators, reference_indicator = 'usnaac0169', historical_run_count = 5):
        try:
            updated_indicators = [indicator[0] for indicator in updated_indicators if indicator != 'usfcst' ]
            data = mb_db_conn.releasedIndicatorChange(updated_indicators)
            indicators = data['indicator_short_info'].unique()
            vendor_keys = data['vendor_key'].unique()
            last_run_id = mb_db_conn.return_latest_run_id()

            ## -- New information released -- ##
            data.rename(columns={"Transformed":"Latest", "period_date":"Period Date", "indicator_short_info": "Indicator"}, inplace=True)
            data["Forecast Error"] = data["Latest"] - data["Forecast"]
            data[["Latest", "Forecast", "Forecast Error"]] = data[["Latest", "Forecast", "Forecast Error"]].round(decimals=2)
            table = data[["Indicator", "Period Date", "Latest", "Forecast", "Forecast Error"]]

            ## -- Get Changed Reference Indicator -- ##
            result_change = mb_db_conn.indicatorResultChange(reference_indicator, historical_run_count)
            result_change = result_change[pd.DatetimeIndex(result_change.index.values).is_quarter_end]
            result_change["Period"] = result_change.index.map(lambda x: "{0}-Q{1}".format(x.year, int(x.month/3)))

            result_change.set_index(['Period'], inplace =True)
            result_change = result_change.round(decimals=2)

            ## -- Put together the message -- ##
            message = "The Nowcast model has been run after updates to the "
            for indicator in indicators:
                vendor_key = data[data["Indicator"] == indicator]['vendor_key'].unique()
                message = message + '''<a href="http://mslinuxdb01.macrosynergy.local#''' + str(vendor_key[0]) + '''">''' + str(indicator) + '''</a>, '''
            message = message[:-2] + " indicators\n\n"

            txt  = "Run Number {0:s} is the result of the latest model run on the latest real data above.".format(str(last_run_id[0]))
            txt += "These are forecasted values. <p>Click <a href= http://mslinuxdb01.macrosynergy.local>here</a> for the full picture</p>"
            message = [message, table.to_html(index=False), result_change.to_html(), txt]

            self.sendMail(message)
        except:
            logging.info("Error retrieving indicator changes: %s", traceback.format_exc())
            raise

    def sendErrorMail(self, message):
        server = smtplib.SMTP(self.config['EMAIL']['email_server'])
        server.starttls()
        sender = self.config['EMAIL']['email_sender']
        receiver = self.config['EMAIL']['email_error_recv']
        msg = EmailMessage()
        msg['Subject'] = "Nowcast Update"
        msg['From'] = sender
        msg['To'] = receiver
        msg.add_alternative("<p> There has been an exception raised in the nowcasting code. Please investigate</p>" + '<p>' +  message + '</p>', subtype='html')
        server.send_message(msg)
        server.quit()

    def sendMail(self, message):
        server = smtplib.SMTP(self.config['EMAIL']['email_server'])
        server.starttls()
        sender = self.config['EMAIL']['email_sender']
        receiver = self.config['EMAIL']['email_receiver']

        msg = EmailMessage()
        msg['Subject'] = "Nowcast Update"
        msg['From'] = sender
        msg['To'] = receiver
        alternative = "<p>" + message[0] + "</p><h3>Real Data</h3><p>" + message[1] + '''</p><h3><a href=http://mslinuxdb01.macrosynergy.local/#usnaac0169>GDP Forecast</a></h3><p>'''
        alternative += message[2] + "</p><p></p><p>" + message[3]
        alternative += '''</p> <p> To see the GDP forecast over time see <a href="http://mslinuxdb01.macrosynergy.local/gdp_fcst_evo.html">here</a> </p>'''
        msg.add_alternative(alternative, subtype='html')

        server.send_message(msg)
        server.quit()

    def LaunchModelScript(self):
        logging.info("Initiate the Model {0}".format(datetime.datetime.now()))

        ## -- The DFM Now-Casting Model -- ##
        #self.model.runModel()

    def SvcDoRun(self):
        logging.info("Checking config")
        self.checkConfig()
        dev = self.config["SETTINGS"].getboolean("development_mode")
        logging.info("Run the service in Development Mode: {0}".format(dev))
        self.model = nowcastModel(dev=dev)

        #  logging.info("Starting.....")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        self.timeout = 60000
        logging.info("Starting SvcDoRun with timeout: %s", self.timeout)
        mb_up = msMBDbInterface(user=self.config['DATABASE']['db_user'],
                                password=self.config['DATABASE']['db_password'],
                                host=self.config['DATABASE']['db_host'], db_name=self.config['DATABASE']['db_name'])
        next_release = mb_up.next_release_date()[0]
        while 1:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("msDbMBService Stopped")
                break
            else:
                try:
                    servicemanager.LogInfoMsg("msDbMBService Querying Db")
                    logging.info("Opening Db Connection within Service: ")
                    now = datetime.datetime.now()
                    incomplete_indicators = mb_up.find_incorrect_release_dates()
                    data_correct = True
                    if incomplete_indicators:
                        for indicator in incomplete_indicators:
                            logging.info("Fixing indicator: %s", str(indicator[0]))
                            c = win32com.client.Dispatch("Macrobond.Connection")
                            d = c.Database
                            ts = d.FetchOneSeries(str(indicator[0]))
                            releaseName = ts.Metadata.GetFirstValue("Release")
                            releaseEntity = d.FetchOneEntity(releaseName)
                            current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
                            next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
                            success = False
                            if next_release:
                                success = mb_up.fix_incomplete_indicator(indicator, next_release)
                                logging.info("Fixing indicator: %s : Complete", str(indicator[0]))
                            if not success:
                                logging.info("Fixing indicator: %s: Incomplete. Checking again in 1hr", str(indicator[0]))
                                self.timeout = 1000 * 60  * 60 * 5# 1s * 60 * 60 = 1hr
                                data_correct = False

                    if next_release.astimezone(self.tz) < now:
                        indicator_updates = mb_up.available_updates()
                    else:
                        # No updates, wait until next release time until checking again.
                        indicator_updates = []
                        time_diff = next_release - now
                        error_margin_min = 15 # Error margin in minutes
                        error_margin = 1000 * 60  * error_margin_min
                        if data_correct:
                            self.timeout = time_diff.total_seconds() * 1000 + error_margin
                        else:
                        	if (time_diff.total_seconds() * 1000 + error_margin) < self.timeout:
                        		self.timeout = time_diff.total_seconds() * 1000 + error_margin

                    if len(indicator_updates) > 0:
                        logging.info("Updates found for: %s", str(indicator_updates))
                        c = win32com.client.Dispatch("Macrobond.Connection")
                        d = c.Database
                        all_series = d.FetchSeries(indicator_updates)
                        logging.info("Series fetched for indicators")
                        for num, indicator_key in enumerate(all_series):
                            ts = all_series[num]
                            releaseName = ts.Metadata.GetFirstValue("Release")
                            releaseEntity = d.FetchOneEntity(releaseName)
                            current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
                            next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
                            if not next_release:
                                next_release = pywintypes.Time(0).replace(year=1900, month=1, day=1)
                            if ts:
                                logging.info("Uploading data for indicator %s", str(indicator_key))
                                mb_up.upload_mb_data(ts, str(indicator_key),  current_release, next_release)
                            logging.info("Upload complete for indicator %s", str(indicator_key))
                        next_release = mb_up.next_release_date()[0]
                        time_diff = next_release - now
                        error_margin_min = 15 # Error margin in minutes
                        error_margin = 1000 * 60  * error_margin_min
                        if (time_diff.total_seconds() * 1000 + error_margin) < self.timeout:
                        		self.timeout = time_diff.total_seconds() * 1000 + error_margin

                        if len([indicator[0] for indicator in indicator_updates if indicator[0].find('usfcst') ]) > 0:
                            self.LaunchModelScript()
                            logging.info("Before email latest run is %s", str(mb_up.return_latest_run_id()))
                            self.indicatorChange(mb_up, indicator_updates)

                    else:
                        logging.info("No updates found, waiting for %s minutes", str(self.timeout / 60000))

                    logging.info("Next Release is: %s", datetime.datetime.strftime(mb_up.next_release_date()[0], '%Y-%m-%d %H:%M'))
                    logging.info("Next check will be: %s", datetime.datetime.strftime(now + datetime.timedelta(seconds = (self.timeout * 0.001)), '%Y-%m-%d %H:%M'))

                except:
                    self.sendErrorMail(str(traceback.format_exc()))
                    logging.info("Connection failed with: %s", traceback.format_exc())
                    servicemanager.LogErrorMsg(traceback.format_exc())
                    pass

def ctrlHandler(ctrlType):
   return True

if __name__ == '__main__':
   win32api.SetConsoleCtrlHandler(ctrlHandler, True)
   win32serviceutil.HandleCommandLine(msServiceMBDb)
