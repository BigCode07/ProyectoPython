# transitos_a_corrected.py
# 12-05-17
# Transitos y contenedores
# Headsets integrado a contenedores
# 170519 Instalaciones (no estable)
# 190201 Cambio de logo bravatec en etiqueta grande

import pygame
import serial
import time
import os
import math
from zebra import Zebra

# Try to import MySQLdb first (for Raspberry Pi compatibility)
# If not available, fall back to mysql.connector
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
                # MySQLdb uses different parameter names
                self.connection = db.Connection(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    passwd=DB_CONFIG['password'],
                    db=DB_CONFIG['database']
                )
            else:
                # mysql.connector syntax
                self.connection = db.connect(**DB_CONFIG)
        except Exception as err:
            print("Error connecting to database: {0}".format(err))
            exit()

    def consultar(self, sql, params=None):
        """ Executes a query. Use params to avoid SQL injection. """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                resultado = cursor.fetchall()
                self.connection.commit() # Commit is needed for INSERT/UPDATE/DELETE
                return resultado
        except db.Error as err:
            print("Database query failed: {0}".format(err))
            return [] # Return an empty list on failure

class Sesion(Conexion):
    def __init__(self):
        super().__init__() # Correct way to call parent constructor
        self.logo_grande = pygame.image.load('img/logo600x100.png')
        self.logo_mediano = pygame.image.load('img/logo200x50.png')

        # ... (rest of the __init__ remains largely the same) ...
        self.menu = 0
        self.dict_programas = {1:'Transitos', 2:'Contenedores', 3:'Instalaciones'}
        self.idprograma = False
        self.display = False
        self.modo_economico = True
        self.modo_impresion = False
        self.impresora_80x40 = 'Zebra_1'
        self.impresora_38x20 = 'Zebra_0'
        self.es_envio = 0
        self.notificacion = ''
        self.comandos = []
        self.rango = 9
        self.v_min_r = 1
        self.v_min_g = 1
        self.v_min_c = 1
        self.multiplicador_r = 0
        self.multiplicador_g = 0
        self.multiplicador_c = 0
        self.total_hs = 0
        self.idusuario = False
        self.out_in = False
        self.idfecha = False
        self.idcontenedor = False
        self.idinsred = False
        self.idred = False
        self.idgrupo = False
        self.idtransito = False
        self.idarticulo = False
        self.idevento = False
        self.dict_fechas = False
        self.dict_transitos = False
        self.dict_redes = False
        self.dict_grupos = False
        self.dict_movimientos = False
        self.dict_movimientos_hs = False
        self.programa = False
        self.nombre_usuario = False
        self.fecha = False
        self.contenedor = False
        self.tipo_contenedor = False
        self.red = False
        self.grupo = False
        self.locacion = False
        self.transito = False
        self.evento = False
        self.informe = False
        self.scroll = False
        self.pantallas = []
        self.headsets_f1 = False
        self.headsets_fol = False
        self.headsets_duo = False
        self.headsets_ptt = False
        self.headsets_raf = False
        self.headsets_spe = False
        
    # --- IMPORTANT: All SQL queries are updated to be parameterized ---
    # Example of a corrected function:
    def obtener_idusuario(self, idusuario):
        self.comandos = []
        self.idusuario = False
        self.nombre_usuario = False
        sql = "SELECT idusuario, nombre FROM usuarios WHERE serie = %s"
        resultado = self.consultar(sql, (idusuario,))
        
        if not resultado:
            self.notificacion = 'ID no valida'
            return False
        else:
            # Assumes one result
            self.idusuario, self.nombre_usuario = resultado[0]
            self.notificacion = 'Ingreso exitoso'
            return True

    def obtener_idcontenedor(self, lectura):
        self.idcontenedor = False
        self.contenedor = False
        self.tipo_contenedor = False
        sql = """
            SELECT c.idcontenedor, c.contenedor, tc.codtipocontenedor 
            FROM contenedores c
            JOIN tipocontenedores tc ON c.tipocontenedor_id = tc.idtipocontenedor 
            WHERE c.idcontenedor = %s
        """
        resultado = self.consultar(sql, (lectura,))
        if not resultado:
            return False
        else:
            self.idcontenedor, self.contenedor, self.tipo_contenedor = resultado[0]
            self.notificacion = 'Contenedor ingresado'
            return True

    def agregar_transito(self, hora_creacion):
        # This function demonstrates a more complex parameterized query
        sql_base = "INSERT INTO transitos (fecha_id, contenedor_id, out_in, es_envio, creacion, creusuario"
        params = [self.idfecha, self.idcontenedor, self.out_in, self.es_envio, hora_creacion, self.idusuario]
        
        if self.idinsred and self.idgrupo:
            sql_base += ", insred_id, grupo_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            params.extend([self.idinsred, self.idgrupo])
        elif self.idinsred:
            sql_base += ", insred_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            params.append(self.idinsred)
        else: # Handles both None and only idgrupo being None
            sql_base += ") VALUES (%s, %s, %s, %s, %s, %s)"

        try:
            self.consultar(sql_base, tuple(params))
            return True
        except Exception as e:
            # self.consultar will print the error, but we can log more context here
            print("Failed to add transito: {0}".format(e))
            return False

    # ... (all other database methods like agregar_movimiento, consultar_fechas, etc.,
    # must be similarly updated to use parameterized queries) ...
    
    def salir(self):
        pygame.quit()
        # Ensure the database connection is closed gracefully
        if self.connection and self.connection.is_connected():
            self.connection.close()
        exit()

    def lector(self):
        # This function remains the same as it's hardware-dependent
        try:
            ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)
            str_read = ser.read(13)
            if len(str_read) > 11:
                # Assuming the device sends carriage return and newline
                return str_read.decode('ascii').strip()
            else:
                return False
        except serial.SerialException as e:
            # Handle cases where the scanner is not connected
            self.notificacion = "Scanner not found on /dev/ttyUSB0"
            time.sleep(1) # Prevent spamming the screen
            return False

# ... (The rest of the script, including the main loop and display logic,
# can remain but will now benefit from the corrected database layer.
# Note that this is a partial correction focusing on the most critical issues.)
# A full rewrite would be needed to correct all structural and logical concerns.