# reimpresion_upc_corrected.py
import os
import mysql.connector as db # Changed from MySQLdb
from zebra import Zebra
import time

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
            self.connection = db.connect(**DB_CONFIG)
        except db.Error as err:
            print(f'No se pudo conectar a la base de datos: {err}')
            self.connection = None # Ensure connection is None on failure

    def consultar(self, sql, params=None):
        if not self.connection:
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                # Use fetchone() when you expect a single result
                return cursor.fetchone()
        except db.Error as err:
            print(f'Error en consulta: {err}')
            return None

class Articulo(Conexion):
    def __init__(self):
        super().__init__()
        self.titulo = 'Bravatec reimpresion etiquetas\n'
        self.impresora = 'Zebra_0'

    def ingresar_comando(self):
        print(self.titulo)
        idarticulo = input('Cod art (0 to exit): ')
        if idarticulo == '0':
            exit()
        if not idarticulo.strip():
            print('Codigo no valido')
            return False
        return idarticulo

    def consultar_articulo(self, idarticulo):
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
        if not resultado:
            print('Articulo inexistente')
            return False
        return resultado

    def imprimir(self, info_etiqueta):
        (idarticulo, codigoequipo, codigo, creacion, codigousuario,
        ingreso_id, modelo, observaciones) = info_etiqueta

        obs = observaciones or '' # More concise way to handle None
        fecha_str = str(creacion).split(' ')[0]
        codart = str(codigo).zfill(4)
        code = str(idarticulo).zfill(11)

        etiqueta = f"""^XA^FWN
^CF0,20
^FO300,80^FDBravatec^FS
^FO460,80^FD{codigoequipo}{codart}^FS
^CF0,16
^FO300,100^FD{fecha_str}^FS
^FO400,100^FD{codigousuario}^FS
^FO420,100^FD{ingreso_id}^FS
^FO460,100^FD{modelo}^FS
^FO300,120^FD{obs}^FS
^BY2
^BUN,40,Y,N,N
^FO310,20
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
            try:
                idarticulo = articulo.ingresar_comando()
                if idarticulo:
                    info_etiqueta = articulo.consultar_articulo(idarticulo)
                    if info_etiqueta:
                        articulo.imprimir(info_etiqueta)
            except KeyboardInterrupt:
                print("\nSaliendo del programa...")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")