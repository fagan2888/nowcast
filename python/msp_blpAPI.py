#!/bin/usr/python3
import logging
from datetime import datetime
import socket
import numpy as np
import pandas as pd
import os
import sys

from optparse import OptionParser
import platform
import blpapi

class bloombergAPI(object):
    def __init__ (self):
        pass

    def checkAuthorisation(self):
        session, apiAuthSvc = self.startService(service="apiauth")
        authorisationRequest = apiAuthSvc.createAuthorizationRequest()
        ## CURRENTLY DOES NOT WORK
        ## NEED identity
        #cid = session.sendAuthorizationRequest(request=authorisationRequest, identity=???)

    def BEQS(self, screenName:str, screenType:str="PRIVATE", fieldNames=["Ticker"]):
        if isinstance(fieldNames, str):
            fieldNames = list(fieldNames)
        self.fieldNames = fieldNames

        ## Bloomberg: BeqsRequst dataset
        session, refDataSvc = self.startService(service="refdata")
        request = refDataSvc.createRequest("BeqsRequest")

        request.set("screenName", screenName)
        request.set("screenType", screenType)
        ## request.set: fieldNames
        #handler = handlerBeqs(fieldNames=fieldNames)

        response = self.executeRequest(
            session = session,
            request = request,
            requestHandler = self.handlerBeqs
            )
        return response

    def handlerBeqs(self, msg):
        responseData = msg.getElement("data")
        securityDataArray = responseData.getElement(1)
        numItems = securityDataArray.numValues()
        response = pd.DataFrame(columns=self.fieldNames)

        count = 0
        for ii in range(0, numItems):
            securityData = securityDataArray.getValueAsElement(ii)
            security = securityData.getElementAsString("security")


            if securityData.hasElement("securityError"):
                msg  =   "security: {0}\n".format(security)
                msg += "{0}".format(securityData.getElement("securityError"))
                logging.error(msg)
            else:
                # REPLACE instead of INSERT ???
                #query = "INSERT INTO {0:s}".format(framename)
                #queryName = "\n\t("
                #queryData = "\n\t("
                data = []
                fieldData = securityData.getElement("fieldData")
                for key in self.fieldNames:
                    #queryName += "{0}, ".format(key) # OBS
                    #queryData += "{0}, ".format(fieldData.getElementAsString(key))
                    data.append( fieldData.getElementAsString(key) )
                #queryName = queryName[:-2] + ")"
                #queryData = queryData[:-2] + ")"
                #query += queryName + "\nVALUES" + queryData
                #query += "\nON DUPLICATE KEY UPDATE "
                #query +="\n;"
                ## EXECUTE SQL STATEMENT
                #self.engine.execute(query)

                count += 1
                response.loc[count]  = data

        return response


    def BDH(self, securitiesNames, fieldNames, startDate:str="19000101", endDate:str=None):
        if isinstance(securitiesNames, str):
            securitiesNames = [securitiesNames]

        if isinstance(fieldNames, str):
            fieldNames = [fieldNames]

        self.fieldNames = fieldNames
        self.countIndex = 0
        ## Bloomberg: ReferenceDataRequest dataset
        session, refDataSvc = self.startService(service="refdata")

        ## HistoricalDataRequest
        request = refDataSvc.createRequest("HistoricalDataRequest")
        for item in securitiesNames:
            request.getElement("securities").appendValue(item)

        for item in fieldNames:
            request.getElement("fields").appendValue(item)

        ## -- Start and End Dates -- ##
        request.set("startDate", startDate)

        if not endDate:
            today = datetime.today()
            endDate = "{0}".format(today.year*10000+today.month*100+today.day)
        request.set("endDate", endDate)

        response = self.executeRequest(
            session = session,
            request = request,
            requestHandler = self.handlerBDH
            )
        return response

    def handlerBDH(self, msg):
        colNames =  ["date", "Ticker"] + self.fieldNames
        response = pd.DataFrame(columns=colNames)

        securityData = msg.getElement("securityData")
        sequenceNumber = np.int64(securityData.getElementAsString("sequenceNumber"))
        security_name = securityData.getElementAsString("security")
        if securityData.hasElement("securityError"):
            msg  =   "security: {0}\n".format(security_name)
            msg += "sequenceNumber: {0}\n".format(sequenceNumber)
            msg += "{0}".format(securityData.getElement("security"))
            logging.error(msg)
        else:
            fieldData = securityData.getElement("fieldData")
            #print(fieldData)
            numItems = fieldData.numValues()
            for ii in range(0, numItems):
                field = fieldData.getValueAsElement(ii)

                self.countIndex += 1
                response.loc[self.countIndex, "Ticker"] = security_name
                for element in field.elements():
                    response.loc[self.countIndex, str(element.name())] = element.getValue()

        return response

    def BDP(self, securitiesNames, fieldNames, conn=None):
        ## Store Output to Datebase
        if conn:
            self.storeDB = True
            self.conn = conn
        else:
            self.storeDB = False

        if isinstance(securitiesNames, str):
            securitiesNames = [securitiesNames]

        if isinstance(fieldNames, str):
            fieldNames = [fieldNames]

        self.fieldNames = fieldNames

        ## Bloomberg: ReferenceDataRequest dataset
        session, refDataSvc = self.startService(service="refdata")

        ## AUTOMATE
        request = refDataSvc.createRequest("ReferenceDataRequest")
        for item in securitiesNames:
            request.getElement("securities").appendValue(item)

        for item in fieldNames:
            request.getElement("fields").appendValue(item)

        response = self.executeRequest(
            session = session,
            request = request,
            requestHandler = self.handlerBDP
            )

        return response

    def handlerBDP(self, msg):
        securityDataArray = msg.getElement("securityData")
        numItems = securityDataArray.numValues()
        response = pd.DataFrame(columns=self.fieldNames)

        for ii in range(0, numItems):
            securityData = securityDataArray.getValueAsElement(ii)
            security = securityData.getElementAsString("security")

            sequenceNumber = np.int64(securityData.getElementAsString("sequenceNumber"))
            if securityData.hasElement("securityError"):
                msg  =   "security: {0}\n".format(security)
                msg += "sequenceNumber: {0}\n".format(sequenceNumber)
                msg += "{0}".format(securityData.getElement("securityError"))
                logging.error(msg)
            else:
                fieldData = securityData.getElement("fieldData")
                for element in fieldData.elements():
                    response.loc[security, str(element.name())] = element.getValue()

        return response

    def executeRequest(self, session, request, requestHandler):
        cid = session.sendRequest(request)
        continueToLoop = True
        store = []
        success = False
        try:
            while (continueToLoop):
                event = session.nextEvent()
                for msg in event:
                    referenceDataResponse = msg.asElement()
                    if cid in msg.correlationIds():
                        if msg.hasElement("responseError"):
                            msg = "Response Error:\n"
                            msg += "{0}".format(referenceDataResponse.getElement("responseError"))
                            logging.error(msg)
                        else:
                            store.append(requestHandler(msg=msg))
                if event.eventType() == blpapi.Event.RESPONSE:
                    msg = "Stopping Event: All data recieved"
                    logging.debug(msg)
                    continueToLoop = False
                    success = True
                    break
            if success:
                response = pd.concat(store)
                return response
        except Exception as error:
            msg = "An error occured:\n{0}".format(error)
            logging.error(msg)
            raise ValueError
        finally:
            session.stop()
            msg = "Connection to Bloomberg closed"
            logging.debug(msg)

    def BDS(self):
        ## Bloomberg: mktdata Current Price Subscription
        refDataSvc = self.startService(service="mktdata")

    def startService(self, service:str="refdata"):
        session = blpapi.Session()
        ## OBS: Build Bloomberg Error
        if not session.start():
            msg = "Error: Unable to start session in Bloomberg"
            raise ValueError(msg)

        if not session.openService("//blp/{0:s}".format(service)):
            msg = "Error unable to open service in Bloomberg"
            raise ValueError(msg)

        refDataSvc = session.getService("//blp/{0:s}".format(service))

        return session, refDataSvc

if __name__ == "__main__":
    now = datetime.now()
    log_filename = 'C:\\BoP\\logs\\mspblpAPI_logfile_{0:s}_{1:%Y%m%d}.log'.format(socket.gethostname(), now)
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)
    msg = "Test main file: {0}".format(__file__)
    logging.info(msg)

    securitiesNames = ["AAPL US Equity", "IBM US Equity", "BLAHBLAH US Equity"]
    fieldNames = ["PX_LAST", "DS002", "VWAP_VOLUME"]
    blp = bloombergAPI()
    if False:
        blp.checkAuthorisation()
    if True:
        response = blp.BDP(securitiesNames=securitiesNames, fieldNames=fieldNames)
        print("\n\nRecieved data")
        print(response)
