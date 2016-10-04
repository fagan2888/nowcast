import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
from msDbaseInterface import msDbInterface
from msDbaseInterface import msMBDbInterface
import win32com.client

class msMBDbService(win32serviceutil.ServiceFramework):
    """A service that polls the database checking when the next release date is"""
    _svc_name_ = "msMBDbService"
    _svc_display_name_ = "Macrosynergy Macrobond DB Service"
    _svc_description_ = "This service queries the Macrosynergy economic indicator database, checks if there are any releases due"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)     
        socket.setdefaulttimeout(60)
        self.stop_requested = False      

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        logging.info('Stopping service ...')
        self.stop_requested = True

    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED(seld._svc_name_, ''))
        self.timeout = 1080000
    
    while 1:
         # Wait for service stop signal, if I timeout, loop again
        rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
        if rc == win32event.WAIT_OBJECT_0:
            servicemanager.LogInfoMsg("msDbMBService Stopped")
            break
        else:
            try:
                mb_up = msMBDbInterface(user = 'dbuser', password = 'Melbourne2016', host = 'mslinuxdb01', db_name = 'ms_econ_Db_DEV')
                indicator_updates = mb_up.available_updates()

                if indicator_updates.len() > 0:
                    logger.info("Updates found")
                    all_series = d.FetchSeries(indicator_updates)
                    for num, indicator_key in enumerate(all_series):
                        ts = all_series[num]
                        releaseName = ts.Metadata.GetFirstValue("Release")
                        releaseEntity = d.FetchOneEntity(releaseName)
                        current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
                        next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
                        if 'bea037_76a067rx_m' != str(indicator_key):
                            mb_up.upload_mb_data(ts, str(indicator_key),  current_release, next_release)                        
            except:
                pass

def ctrlHandler(ctrlType):
   return True
                          
if __name__ == '__main__':   
   win32api.SetConsoleCtrlHandler(ctrlHandler, True)   
   win32serviceutil.HandleCommandLine(msMBDbService)

