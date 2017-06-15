#!/bin/usr/python3
import logging
import socket
import datetime
import os
if __name__ == "__main__":
    now = datetime.datetime.now()
    os.chdir("/repos/Nowcast/")
    log_filename = '/repos/Nowcast/logs/{0:%Y-%m-%d}_MS_Investigate_logfile_{1}.log'.format(now, socket.gethostname())
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

import numpy as np
import pandas as pd
import mysql.connector
import sys
import configparser
import traceback
import sqlalchemy
from msDbaseInterface import msDbInterface


class buildDatabase(msDbInterface):
    def __init__(self, configPath:str='/repos/nowcast/config/', dev:bool=True):
        ## re-tweek to give model_id:int as input?
        self.configPath = configPath
        self.dev = dev
        self.getConfig()
        self.engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)

    def getConfig(self):
        config = configparser.ConfigParser()
        config.read(self.configPath + 'configNowcasting.ini')

        ## -- DATABASE -- ##
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname = "DATABASE_UAT"
        self.user = config[dbname].get("db_user")
        self.password = config[dbname].get("db_password")
        self.db_name = config[dbname].get("db_name")
        self.host = config[dbname].get("db_host")

        ## -- MODELS -- ##
        self.modelID = {}
        for key in config["MODELS"]:
            self.modelID[key] = config["MODELS"].getint(key)

    def executeSQL(self, filename:str, connection:sqlalchemy.engine.base.Connection):
        queries = [""]
        count = 0
        with open(filename) as f:
            for line in f.readlines():
                line = line.replace("\n", " ").replace("\t", " ")
                if ("--" not in line[0:2]) and (len(line)>0):
                    if (";" not in line):
                        queries[count] += line
                    else:
                        queries[count] += line.split(";")[0] + ";"
                        count += 1
                        queries.append(line.split(";")[1])
                elif ("--" not in line[0:2]) and ("--" in line):
                    queries[count] += line.split("--")[0]
        queries = [ii for ii in queries if len(ii)>0]
        print(queries)
        for query in queries:
            print(query)
            #response = connection.execute(query)
            #response.close()

    def dropTables(self):
        ## OBS: DOES NOT WORK!!!
        response = input("Are you sure you want to drop the tables for {0} (Y/N): ".format(self.db_name))
        if response.upper() == "Y":
            connection = self.engine.connect()
            print("Drop tables")
            self.executeSQL(filename="sql/create/drop_tables.sql", connection=connection)

            # 1) Recreate: meta_table
            print("Create Meta tables")
            self.executeSQL(filename="sql/create/create_meta_tables.sql", connection=connection)

            # 2) Recreate: data_table
            print("Create data tables")
            self.executeSQL(filename="sql/create/create_data_tables.sql", connection=connection)


            # 3) Recreate: model_tables
            print("Create model tables")
            self.executeSQL(filename="sql/create/create_model_tables.sql", connection=connection)

            # 4) Recreate: output_tables
            print("Create output tables")
            self.executeSQL(filename="sql/create/create_output_tables.sql", connection=connection)

            # 5) Recreate: forecast_tables
            #self.executeSQL(filename="sql/create/create_forecasts_tables.sql", connection=connection)
            self.populateTables()
        else:
            print("Not dropping the tables")

    def executeSQLUpload(self, data:pd.core.frame.DataFrame, select:list, tableName:str):
        query = """INSERT INTO {0:s} ({1:s})
                VALUES ({2:s})
                ON DUPLICATE KEY UPDATE {3:s};
                """.format(tableName, ", ".join(select), ", ".join(["%s" for ii in select]), ", ".join(["{0}={0}".format(ii) for ii in select]))
        df_to_tuple = [tuple(row[select].values) for index, row in data.iterrows()]
        self.cursor.executemany(query, df_to_tuple)
        self.cnx.commit()

    def populateDataTables(self):
        sources = pd.read_excel("data/master-datasource.xlsx", header=0, sheetname="sources")
        select = ["source_id", "source_name", "source_description"]
        self.executeSQLUpload(data=sources, select=select, tableName="data_sources")

        variableID = pd.read_excel("data/master-datasource.xlsx", header=0, sheetname="variable_id")
        variableID = pd.merge(variableID, sources[["source_id", "source_name"]], on="source_name", how='left')
        select = ["variable_id", "variable_name", "variable_description", "source_id", "dataset", "frequency_id", "country_id", "indicator_type"]
        self.executeSQLUpload(data=variableID, select=select, tableName="data_variable_id")

        indicators = pd.read_excel("data/master-datasource.xlsx", header=0, sheetname="indicators")
        indicators = pd.merge(indicators, sources[["source_name", "source_id"]], left_on="provider_name", right_on="source_name", how='left')
        indicators.rename(columns={"source_id":"provider_id"}, inplace=True)
        select = ["indicator_id", "provider_id", "vendor_key", "variable_id", "active"]
        self.executeSQLUpload(data=indicators, select=select, tableName="data_indicators")

    def populateModelTables(self):
        modelReferences = pd.read_excel("data/master-models.xlsx", header=0, sheetname="model_references")
        select = ["model_name", "target_country_id", "target_variable_id", "model_type", "created_by"]
        self.executeSQLUpload(data=modelReferences, select=select, tableName="model_references")


        modelControls = pd.read_excel("data/master-models.xlsx", header=0, sheetname="model_controls")
        query = "SELECT variable_id, variable_name FROM meta_control_variables;"
        controls = pd.read_sql(sql=query, con=self.engine)
        query = "SELECT model_id, model_name FROM model_references;"
        model = pd.read_sql(sql=query, con=self.engine)
        modelControls = pd.merge(modelControls, controls[["variable_id", "variable_name"]], left_on="control_variable_name", right_on="variable_name", how="left")
        modelControls = pd.merge(modelControls, model, on="model_name", how='left')
        modelControls.rename(columns={"variable_id":"control_id"}, inplace=True)
        select = ["model_id", "control_id", "control_values"]
        self.executeSQLUpload(data=modelControls, select=select, tableName="model_controls")

        modelIndicators = pd.read_excel("data/master-models.xlsx", header=0, sheetname="model_indicators")
        modelIndicators = pd.merge(modelIndicators, model, on="model_name")
        select = ["model_id", "indicator_id", "transformation_code", "presentation_code"]
        self.executeSQLUpload(data=modelIndicators, select=select, tableName="model_indicators")


if __name__ == "__main__":
    while True:
        path = os.path.split(os.getcwd())
        if path[1] == "Nowcast":
            break
        elif "Nowcast" in path[0]:
            os.chdir(path[0])
        else:
            raise ValueError("Nowcasting not in path")
    db = buildDatabase()
    db.populateDataTables()
    db.populateModelTables()
