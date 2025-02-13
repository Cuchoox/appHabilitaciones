import pandas as pd
from sqlalchemy import create_engine, text
import pymysql

def upload_excel_to_db(file_path, company_name):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        
        # Renombrar la columna para que coincida con la base de datos
        df.rename(columns={'Documento': 'nombre_requisito'}, inplace=True)
        
        # Agregar la columna de empresa_id manualmente (ID de CMPC = 2)
        df['empresa_id'] = 2
        
        # Agregar la categoría con valor 'Personal' a todos los registros
        df['categoria'] = 'Personal'
        
        # Conexión a la base de datos
        engine = create_engine('mysql+pymysql://root:Cucho123@localhost/Mci')
        
        # Verificar datos antes de subir
        print("Datos a subir:")
        print(df.head())
        
        # Subir a la base de datos en la tabla correcta
        df.to_sql('requisitos_empresa', con=engine, if_exists='append', index=False)
        print("Datos subidos correctamente a REQUISITOS_EMPRESA.")
    
    except Exception as e:
        print(f"Error al subir datos: {e}")

if __name__ == "__main__":
    file_path = r"C:\\Users\\Cucho\\Downloads\\Documentos_Clasificados.xlsx"  # Ruta del archivo Excel
    empresa = 'CMPC'
    upload_excel_to_db(file_path, empresa)
