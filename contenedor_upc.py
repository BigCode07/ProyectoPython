# -*- coding: utf-8 -*-
# contenedor_upc_corrected.py
import os
from zebra_compat import Zebra
import time

# Try to import MySQLdb first (for Raspberry Pi compatibility)
try:
    import MySQLdb as db
    USE_MYSQLDB = True
except ImportError:
    import mysql.connector as db
    USE_MYSQLDB = False

# --- Configuration ---
DB_CONFIG = {
    'host': '192.168.11.3',
    'port': 3306,
    'user': 'root',
    'password': 'bravatec',
    'database': 'bravatec'
}

class Conexion:
    def __init__(self):
        try:
            if USE_MYSQLDB:
                self.connection = db.Connection(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    passwd=DB_CONFIG['password'],
                    db=DB_CONFIG['database']
                )
            else:
                self.connection = db.connect(**DB_CONFIG)
        except Exception as err:
            print('No se pudo conectar a la base de datos: {0}'.format(err))
            self.connection = None

    def consultar(self, sql, params=None):
        if not self.connection:
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchone()
        except db.Error as err:
            print('Error en consulta: {0}'.format(err))
            return None

class Contenedor(Conexion):
    def __init__(self):
        super().__init__()
        self.titulo = 'Bravatec Contenedores (salir: 999)'
        self.impresora = 'Zebra_0'

    def ingresar_comandos(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(self.titulo)
        cod_tipo = input('Codigo de tipo de contenedor: ')
        if cod_tipo == '999':
            return None, None
        
        num_cont = input('Numero de contenedor: ')
        if num_cont == '999':
            return None, None
            
        if not cod_tipo.strip() or not num_cont.strip():
            print('Entrada no valida')
            time.sleep(1)
            return False, False
            
        return cod_tipo, num_cont

    def consultar_contenedor(self, codigocontenedor, contenedor):
        sql = """
            SELECT c.idcontenedor, c.contenedor, c.tipocontenedor_id 
            FROM contenedores c
            WHERE c.tipocontenedor_id = %s AND c.contenedor = %s
        """
        resultado = self.consultar(sql, (codigocontenedor, contenedor))
        if not resultado:
            print('Contenedor inexistente')
            return False
        return resultado

    def imprimir(self, info_lista):
        idcontenedor, contenedor, codigocontenedor = info_lista
        code = str(idcontenedor).zfill(11)
        
        etiqueta = f"""^XA
^CF0,25
^FWN
^FO270,30^FDBravatec^FS
^CF0,14
^FO310,50^FDRacing^FS
^FWN
^CF0,80
^FO270,70^FD{contenedor}^FS
^BY2
^BU,100,Y,N,N
^FO370,30
^FD{code}^FS
^XZ"""
        try:
            z = Zebra(self.impresora)
            z.output(etiqueta)
            print(f"Etiqueta para contenedor {contenedor} enviada.")
        except Exception as e:
            print(f"Error al imprimir: {e}")

if __name__ == "__main__":
    cont = Contenedor()
    if not cont.connection:
        print("Saliendo del programa por error de conexi�n.")
    else:
        while True:
            cod_tipo, num_cont = cont.ingresar_comandos()
            if cod_tipo is None:
                print("Saliendo.")
                break
            if cod_tipo and num_cont:
                info_etiqueta = cont.consultar_contenedor(cod_tipo, num_cont)
                if info_etiqueta:
                    cont.imprimir(info_etiqueta)
                    time.sleep(2) # Pause before clearing screen again