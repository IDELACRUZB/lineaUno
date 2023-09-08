import pandas as pd
import pymysql
import json
from datetime import datetime

class ReportService:
    def loadData(self,filePath, tableName : str, dbName : str, properties : {}, renameColumns : {}, converters : []):
        filePath = filePath

        # Nombre de la tabla
        dbTable = tableName

        percentage = {}
        for convert in converters:
            percentage[convert] = self.convertToPercentage
        
        # Lee el archivo EXCEL con pandas
        #df = pd.read_excel( filePath,  sheet_name=0, engine='openpyxl', skiprows=0, dtype=properties, converters=percentage)
        df = pd.read_csv(filePath, sep=',', header=0)

        #df =df.loc[df.iloc[:, 0] != "~Total"]

        # Renombrar la columna        
        df.columns = df.columns.str.strip()
        df.rename(columns=renameColumns, inplace=True)

        # Formatear las columnas
        df = df.fillna(value='')
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(r'^\d+\.-\s*', '', regex=True)
        df.columns = df.columns.str.replace('\n', '')
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        df.columns = df.columns.str.lstrip('_')

        #print(df.columns)
        #for i in df.columns:
        #    print(i)
        #exit()
        # Configurar la conexión a la base de datos
        properties = self.getProperties()
        conn = pymysql.connect(
            host=properties['DB_HOST'],
            database= dbName,
            user=properties['DB_USER'],
            password=properties['DB_PASSWORD'],
            port=3306
        )

        try:
            # Crear un cursor y comenzar una transacción
            cur = conn.cursor()
            cur.execute("START TRANSACTION;")
            #cur.execute(f"TRUNCATE TABLE {dbTable};")

            sqlHeading = "`,`".join(df.columns)

            #['nombre_1','nombre_2','nombre_3']
            #insert into dbTable (nombre_1,nombre_2,nombre_3) values (1,2,3)

            num_cols = len(df.columns) 
            sqlValues = ','.join(['%s'] * num_cols)

            #insert into dbTable (nombre_1,nombre_2,nombre_3) values (%,%,%)


            # Insertar los datos en la base de datos    
            for index, row in df.iterrows():

                # Extraemos la informacion de la fila para el INSERT
                values = []
                for key,value in row.items():            
                    not_default = []
                    
                    if key in not_default:                
                        value = None if not value or pd.isna(value) else value

                    values.append(value)    
                    
                consulta = "INSERT INTO "+dbTable+" (`" + sqlHeading + "`) VALUES ("+sqlValues+")"  

                #consulta = "insert into dbTable (nombre_1,nombre_2,nombre_3) values (%,%,%)"
                                 
                cur.execute(consulta, values)   
                
            # Confirmar la transacción si todo ha ido bien
            conn.commit()
                
            # Obtener la carpeta del usuario actual
            """if(os.path.exists(filePath)):
                os.remove(filePath)"""
            
            print('Se ejecuto correctamente la consulta: ' + dbName + " / " + tableName)

        except Exception as e:
            # Revertir la transacción si hay un error            
            conn.rollback()    
            print("Hubo un error al importar la informacion: " + str(e) )
            return 400 
            
        finally:
            # Cerrar la conexión a la base de datos
            cur.close()
            conn.close()

        return 200
    
    def getProperties(self):
        config_data = None
        with open('config.json') as config_file:
            config_data = json.load(config_file)

        return config_data
    
    def convertToPercentage(self,x):
        return "{:.2f}%".format(x * 100)
    