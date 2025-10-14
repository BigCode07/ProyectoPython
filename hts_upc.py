# hts_upc_corrected.py
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
            print(f'No se pudo conectar a la base de datos: {err}')
            self.connection = None

    def consultar(self, sql, params=None):
        if not self.connection:
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                # Use fetchone() when expecting a single result
                return cursor.fetchone()
        except db.Error as err:
            print(f"Error en la consulta: {err}")
            return None

class Articulo(Conexion):
    def __init__(self):
        super().__init__()
        self.titulo = 'Bravatec reimpresion etiquetas\n'
        self.impresora = 'Zebra_0'

    def clear_screen(self):
        """Clears the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def ingresar_comando(self):
        self.clear_screen()
        print(self.titulo)
        idarticulo = input('Cod art (0 to exit): ') # Changed to input for Python 3
        if idarticulo == '0':
            exit()
        if not idarticulo.strip():
            print('Codigo no valido')
            time.sleep(1)
            return False
        return idarticulo

    def consultar_articulo(self, idarticulo):
        # Parameterized query to prevent SQL injection
        sql = """
            SELECT a.idarticulo, e.codigoequipo, a.codigo, a.creacion, 
                u.codigousuario, a.ingreso_id, m.modelo, a.observaciones 
            FROM articulos a
            JOIN modelos m ON a.modelo_id = m.idmodelo
            JOIN equipos e ON m.equipo_id = e.idequipo
            JOIN usuarios u ON a.creusuario = u.idusuario 
            WHERE a.idarticulo = %s
        """
        resultado = self.consultar(sql, (idarticulo,))
        if not resultado: # Modern way to check for empty result
            print('Art. inexistente')
            return False
        return resultado

    def imprimir(self, info_etiqueta):
        (idarticulo, codigoequipo, codigo, creacion, codigousuario,
        ingreso_id, modelo, observaciones) = info_etiqueta

        codart = str(codigo).zfill(4)
        code = str(idarticulo).zfill(11)
        obs = observaciones or ''

        # Using an f-string for better readability
        etiqueta = f"""^XA
^CF0,22
^FWN
^FO270,20^FDBravatec^FS
^FO270,40^FDBateria^FS
^FO270,110^GB700,1,3^FS
^FO270,110^FDBravatec^FS
^CF0,20
^FO270,75^FD{codigoequipo}{codart}^FS
^FO290,145^FD{codigoequipo}{codart}^FS
^CF0,15
^FO270,60^FD{modelo}^FS
^FO270,130^FD{modelo}^FS
^BY2
^BU,120,Y,N,N
^FO360,20
^FD{code}^FS
^XZ"""
        try:
            z = Zebra(self.impresora)
            z.output(etiqueta)
            print(f"Etiqueta para {idarticulo} enviada a la impresora.")
        except Exception as e:
            print(f"Error al imprimir: {e}")

if __name__ == "__main__":
    articulo = Articulo()
    if not articulo.connection:
        print("Saliendo del programa por error de conexi�n.")
    else:
        while True:
            idarticulo = articulo.ingresar_comando()
            if idarticulo:
                # Scanners can append extra characters; this cleans the input.
                if len(idarticulo) == 12:
                    idarticulo = idarticulo[:-1]
                info_etiqueta = articulo.consultar_articulo(idarticulo)
                if info_etiqueta:
                    articulo.imprimir(info_etiqueta)
                    time.sleep(1)