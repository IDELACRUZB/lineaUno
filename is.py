import os
from util.email import Email
import json
import glob
from datetime import datetime
from service.ReportService import ReportService

mReport = ReportService()
properties = mReport.getProperties()

# Obtenemos el nombre del archivo
# filePath = r'/home/renovaciones/3ERIZA_RENOVACIONES_ALL.csv'
ROOT_PATH = properties['LOAD_PATH']

FILES_PATH = []
FILES_NOT_FOUND = []

jsonDataReports = 'reports.json'

with open(jsonDataReports, "r") as json_file:
    data = json.load(json_file)

    for platform in data['lineaUno']: 
        for campaign in data['lineaUno'][str(platform)]:
            campana = campaign["campaign"]
            for reporte in campaign["reports"]:
                codigo = reporte["code"]
                properties = reporte["properties"]
                print("Reporte:", codigo)
                
                directoryPath = ROOT_PATH  + campana + "\\" + platform + "\\" + codigo
                print('tabla: '+ codigo)