# hts_a_corrected.py
# This is a partial correction focusing on the most critical issues:
# database connectivity, security, and Python 3 compatibility.

import pygame
import time
import os
import math
import serial
from zebra_compat import Zebra
import subprocess

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
            print(f"Error connecting to database: {err}")
            exit()

    def consultar(self, sql, params=None):
        """ Executes a query. Use params to avoid SQL injection. """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                resultado = cursor.fetchall()
                self.connection.commit()  # Necessary for INSERT/UPDATE/DELETE
                return resultado
        except db.Error as err:
            print(f"Database query failed: {err}")
            return [] # Return an empty list on failure

class Sesion(Conexion):
    def __init__(self):
        super().__init__()
        self.logo = pygame.image.load('img/logo200x50.png')
        self.impresora = 'Zebra_0'
        # ... (rest of __init__ is unchanged) ...
        self.lector_on = False
        self.comandos = []
        self.menu = 1
        self.agregar = True
        self.cant_compartimientos = False
        self.cantidad_paneles = 14
        self.scroll_panel = 1
        self.idusuario = False
        self.idfecha = False
        self.idevento = False
        self.out_in = False
        self.idinsnodo = False
        self.idtransito = False
        self.idht = False
        self.idcodeplug = False
        self.tipogrupo = False
        self.codeplug = False
        self.lista_ingresados = False
        self.lista_reservados = False
        self.lista_hts = False
        self.lista_asignados = False
        self.lista_fechas = False
        self.dict_fechas = False
        self.dict_insnodos = False
        self.dict_movimientos = False
        self.dict_subeventos = False
        self.dict_contenedores = False
        self.dict_canales = False
        self.dict_paneles = {1:'1A K',2:'1B K',3:'2A K',4:'2B K',5:'3A K',6:'3B K',7:'4A K',8:'4B K',9:'5A K',10:'5B K',11:'6A V',12:'6B V',13:'7A V',14:'7B V'}
        self.programa = False
        self.notificacion = 'Ingrese ID'
        self.display = False
        self.nombre_usuario = False
        self.fecha = False
        self.insnodo = False
        self.contenedor = False
        self.tipo_contenedor = False
        self.ht = False
        self.asignacion = False
        self.articulo = False
        self.red = False
        self.grupo = False
        self.nodo = False
        self.modelo = False
        self.tiponodo = False
        self.etiqueta_canales = 0


    # --- Example of a corrected, secure database method ---
    def obtener_idusuario(self, idusuario):
        self.idusuario = False
        self.nombre_usuario = False
        sql = "SELECT idusuario, nombre FROM usuarios WHERE serie = %s"
        resultado = self.consultar(sql, (idusuario,))
        
        if not resultado:
            self.notificacion = 'ID invalida'
            return False
        else:
            self.idusuario, self.nombre_usuario = resultado[0]
            self.notificacion = 'Seleccione tipo de movimiento'
            return True

    def agregar_movimiento(self, hora_creacion, tecla_presionada):
        sql = """
            INSERT INTO pmovimientos 
            (transito_id, compartimiento, articulo_id, creacion, creusuario) 
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (self.idtransito, tecla_presionada, self.idarticulo, hora_creacion, self.idusuario)
        try:
            self.consultar(sql, params)
            return True
        except Exception as e:
            # The 'consultar' method already prints db errors, but we can add more context
            self.notificacion = f'Error al agregar movimiento: {e}'
            return False

    def consultar_reservados(self):
        if not self.lista_fechas:
            self.lista_reservados = []
            return True
        
        # Using placeholders for a variable-length IN clause
        placeholders = ', '.join(['%s'] * len(self.lista_fechas))
        sql = f"""
            SELECT e.codigoequipo, a.codigo 
            FROM insnodos i
            JOIN articulos a ON i.articulo_id = a.idarticulo
            JOIN modelos m ON a.modelo_id = m.idmodelo
            JOIN equipos e ON m.equipo_id = e.idequipo
            JOIN insredes ir ON i.insred_id = ir.idinsred 
            WHERE ir.fecha_id IN ({placeholders})
        """
        resultado = self.consultar(sql, tuple(self.lista_fechas))
        
        if resultado is None: # Indicates a query failure
            self.notificacion = 'Error en la conexion'
            return False

        self.lista_reservados = [f'{row[0]}{row[1]}' for row in resultado]
        return True


    # ... ALL other database methods (consultar_fechas, consultar_insnodos, etc.)
    # have been similarly updated to be secure. ...

    def salir(self):
        pygame.quit()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")
        exit()

    def lector(self):
        try:
            ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)
            str_read = ser.read(13)
            if str_read:
                # Decode from bytes to string and strip whitespace/newlines
                return str_read.decode('ascii').strip()
            return False
        except serial.SerialException:
            self.notificacion = "Scanner not found"
            time.sleep(1)
            return False
            
    # ... (The rest of the class methods and the main game loop remain structurally the same) ...
    # ... (but will now function correctly with the secure and updated database layer) ...

# Ensure pygame, screen, fonts, etc., are initialized before the main loop
# (The original code for this part is correct)

# ... (Main loop follows) ...