import win32serviceutil
import win32service
import win32event
import win32api
import servicemanager
import socket
import datetime
import logging
import traceback
from msDbaseInterface import msDbInterface
from msDbaseInterface import msMBDbInterface
import msLogConfig
import win32com.client
import getpass
import pywintypes

class msMBDbService(win32serviceutil.ServiceFramework):
    """A service that polls the database checking when the next release date is"""
    _svc_name_ = "msMBDbService"
    _svc_display_name_ = "Macrosynergy Macrobond DB Service"
    _svc_description_ = "This service queries the Macrosynergy economic indicator database, checks if there are any releases due"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
      #  logging.info("Initiating")

    def SvcStop(self):
      #  logging.info("Stopping....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
      #  logging.info("Starting.....")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        self.timeout = 60000

        while 1:
            logging.info("Stepping into loop")
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("msDbMBService Stopped")
                break
            else:
                try:
                    servicemanager.LogInfoMsg("msDbMBService Querying Db")
                    logging.info("Opening Db Connection within Service")
                    mb_up = msMBDbInterface(user = 'dbuser', password = 'Melbourne2016', host = 'mslinuxdb01', db_name = 'ms_econ_Db_DEV')
                    now = datetime.datetime.now()
                    data_correct = True
                    incomplete_indicators = mb_up.find_incorrect_release_dates()
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
                                logging.info("Fixing indicator: %s: Incomplete", str(indicator[0]))
                                data_correct = False
                            if not data_correct:
                                self.timeout = 1000 * 60  * 65 # 1s * 60 * 60 = 1hr

                    next_release = mb_up.next_release_date()[0]
                    logging.info("Next release: %s", str(next_release))
                    if next_release < now:
                        indicator_updates = mb_up.available_updates()
                    else:
                        # No updates, wait until next release time until checking again.
                        indicator_updates = []
                        time_diff = next_release - now
                        error_margin = 1000 * 60  * 60 # Error margin of an hour
                        if data_correct:
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
                    else:
                        logging.info("No updates found, waiting for %s minutes", str(self.timeout / 60000))

                    logging.info("Next check will be: %s", datetime.datetime.strftime(now + datetime.timedelta(seconds = (self.timeout * 0.001)), '%Y-%m-%d %H:%M'))

                except:
                    logging.info("Connection failed with: %s", traceback.format_exc())
                    servicemanager.LogErrorMsg(traceback.format_exc())
                    pass

def ctrlHandler(ctrlType):
   return True

if __name__ == '__main__':
   win32api.SetConsoleCtrlHandler(ctrlHandler, True)
   win32serviceutil.HandleCommandLine(msMBDbService)
