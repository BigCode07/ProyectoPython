# universal_scanner.py
# Scanner universal compatible con cualquier lectora de código de barras
# Permite entrada manual y automática por scanner

import os
import sys
import time
import threading
import queue
from datetime import datetime
import mysql.connector as db
from zebra import Zebra

# --- Configuración ---
DB_CONFIG = {
    'host': '192.168.11.3',
    'port': 3306,
    'user': 'root',
    'password': 'bravatec',
    'database': 'bravatec'
}

class UniversalScanner:
    """
    Clase para manejar entrada de códigos desde cualquier fuente:
    - Teclado manual
    - Cualquier lectora de código de barras (actúan como teclado)
    - Lectoras seriales (USB/RS232)
    """
    
    def __init__(self):
        self.input_queue = queue.Queue()
        self.running = True
        self.last_input_time = 0
        self.scanner_speed_threshold = 0.1  # 100ms entre caracteres indica scanner
        
    def detect_input_source(self, input_text, input_time):
        """
        Detecta si la entrada viene de un scanner o del teclado manual
        basándose en la velocidad de entrada
        """
        time_diff = input_time - self.last_input_time
        self.last_input_time = input_time
        
        # Si el tiempo entre el último carácter y enter es muy corto, es scanner
        if len(input_text) > 3 and time_diff < self.scanner_speed_threshold:
            return "scanner"
        else:
            return "manual"
    
    def get_input(self, prompt="Escanee o ingrese código: "):
        """
        Obtiene entrada universal - funciona con scanner o teclado
        """
        print(prompt, end='', flush=True)
        start_time = time.time()
        
        try:
            # input() funciona tanto para teclado como para scanners USB/HID
            # Los scanners USB aparecen como teclado al sistema
            user_input = input().strip()
            end_time = time.time()
            
            if not user_input:
                return None, "empty"
            
            # Detectar fuente de entrada
            source = self.detect_input_source(user_input, end_time - start_time)
            
            # Limpiar códigos que vienen con caracteres extra del scanner
            cleaned_input = self.clean_barcode_input(user_input)
            
            return cleaned_input, source
            
        except KeyboardInterrupt:
            return None, "exit"
        except Exception as e:
            print(f"Error en entrada: {e}")
            return None, "error"
    
    def clean_barcode_input(self, raw_input):
        """
        Limpia la entrada de caracteres especiales que algunos scanners añaden
        """
        # Remover caracteres de control comunes
        cleaned = raw_input.replace('\r', '').replace('\n', '').replace('\t', '')
        
        # Algunos scanners añaden caracteres al final
        if len(cleaned) > 11 and cleaned.endswith('1'):
            cleaned = cleaned[:-1]
        
        # Remover espacios y caracteres no imprimibles
        cleaned = ''.join(char for char in cleaned if char.isprintable()).strip()
        
        return cleaned

class Conexion:
    def __init__(self):
        try:
            self.connection = db.connect(**DB_CONFIG)
            print("Conexión a base de datos establecida")
        except db.Error as err:
            print(f"Error conectando a base de datos: {err}")
            self.connection = None

    def consultar(self, sql, params=None):
        if not self.connection:
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                if sql.strip().lower().startswith(('insert', 'update', 'delete')):
                    self.connection.commit()
                    return cursor.rowcount
                else:
                    return cursor.fetchone()
        except db.Error as err:
            print(f"Error en consulta: {err}")
            return None

    def consultar_multiple(self, sql, params=None):
        if not self.connection:
            return []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
        except db.Error as err:
            print(f"Error en consulta múltiple: {err}")
            return []

class BravatecScanner(Conexion):
    def __init__(self):
        super().__init__()
        self.scanner = UniversalScanner()
        self.impresora_grande = 'Zebra_1'  # 80x40mm
        self.impresora_chica = 'Zebra_0'   # 38x20mm
        self.modo_actual = None
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_menu_principal(self):
        self.clear_screen()
        print("=" * 50)
        print("    BRAVATEC - SCANNER UNIVERSAL")
        print("=" * 50)
        print("1. Reimpresión de Artículos")
        print("2. Reimpresión de Contenedores") 
        print("3. Etiquetas de Headsets")
        print("4. Códigos Personalizados")
        print("5. Test de Scanner")
        print("0. Salir")
        print("=" * 50)
    
    def seleccionar_modo(self):
        while True:
            self.mostrar_menu_principal()
            opcion, source = self.scanner.get_input("Seleccione opción: ")
            
            if opcion == '0':
                return None
            elif opcion == '1':
                return 'articulos'
            elif opcion == '2':
                return 'contenedores'
            elif opcion == '3':
                return 'headsets'
            elif opcion == '4':
                return 'personalizado'
            elif opcion == '5':
                return 'test'
            else:
                print("Opción inválida. Presione Enter...")
                input()
    
    def modo_articulos(self):
        """Reimpresión de etiquetas de artículos"""
        self.clear_screen()
        print("=" * 50)
        print("    REIMPRESIÓN DE ARTÍCULOS")
        print("=" * 50)
        print("Escanee código de artículo o ingrese manualmente")
        print("(0 para volver al menú principal)")
        print("=" * 50)
        
        while True:
            codigo, source = self.scanner.get_input("\nCódigo de artículo: ")
            
            if not codigo or codigo == '0':
                break
            
            # Indicar fuente de entrada
            print(f"Entrada: {source.upper()}")
            
            # Consultar artículo
            info_articulo = self.consultar_articulo(codigo)
            if info_articulo:
                self.imprimir_etiqueta_articulo(info_articulo)
            else:
                print("Artículo no encontrado")
                
            time.sleep(2)
    
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
        return self.consultar(sql, (idarticulo,))
    
    def imprimir_etiqueta_articulo(self, info_articulo):
        (idarticulo, codigoequipo, codigo, creacion, codigousuario,
        ingreso_id, modelo, observaciones) = info_articulo

        obs = observaciones or ''
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
            z = Zebra(self.impresora_chica)
            z.output(etiqueta)
            print(f"✓ Etiqueta para artículo {idarticulo} enviada a impresora")
        except Exception as e:
            print(f"Error al imprimir: {e}")
    
    def modo_contenedores(self):
        """Reimpresión de etiquetas de contenedores"""
        self.clear_screen()
        print("=" * 50)
        print("    REIMPRESIÓN DE CONTENEDORES")
        print("=" * 50)
        print("Escanee código de contenedor o ingrese manualmente")
        print("(0 para volver al menú principal)")
        print("=" * 50)
        
        while True:
            codigo, source = self.scanner.get_input("\nCódigo de contenedor: ")
            
            if not codigo or codigo == '0':
                break
                
            print(f"📱 Entrada: {source.upper()}")
            
            # Para contenedores podemos necesitar tipo y número por separado
            if source == "manual":
                num_cont, _ = self.scanner.get_input("Número de contenedor: ")
                if num_cont:
                    info_contenedor = self.consultar_contenedor(codigo, num_cont)
                else:
                    continue
            else:
                # Si es scanner, asumir que el código completo está en una sola lectura
                info_contenedor = self.consultar_contenedor_por_id(codigo)
            
            if info_contenedor:
                self.imprimir_etiqueta_contenedor(info_contenedor)
            else:
                print("Contenedor no encontrado")
                
            time.sleep(2)
    
    def consultar_contenedor(self, tipo, numero):
        sql = """
            SELECT c.idcontenedor, c.contenedor, c.tipocontenedor_id 
            FROM contenedores c
            WHERE c.tipocontenedor_id = %s AND c.contenedor = %s
        """
        return self.consultar(sql, (tipo, numero))
    
    def consultar_contenedor_por_id(self, id_contenedor):
        sql = """
            SELECT c.idcontenedor, c.contenedor, c.tipocontenedor_id 
            FROM contenedores c
            WHERE c.idcontenedor = %s
        """
        return self.consultar(sql, (id_contenedor,))
    
    def imprimir_etiqueta_contenedor(self, info_contenedor):
        idcontenedor, contenedor, tipocontenedor = info_contenedor
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
            z = Zebra(self.impresora_chica)
            z.output(etiqueta)
            print(f"✓ Etiqueta para contenedor {contenedor} enviada a impresora")
        except Exception as e:
            print(f"Error al imprimir: {e}")
    
    def modo_test(self):
        """Modo de prueba del scanner"""
        self.clear_screen()
        print("=" * 50)
        print("    TEST DE SCANNER")
        print("=" * 50)
        print("Este modo permite probar la lectura de códigos")
        print("Se mostrará la fuente detectada y el código limpio")
        print("(0 para volver al menú)")
        print("=" * 50)
        
        while True:
            codigo, source = self.scanner.get_input("\n🔍 Escanee o escriba código: ")
            
            if not codigo or codigo == '0':
                break
            
            print(f"Fuente detectada: {source.upper()}")
            print(f"Código recibido: '{codigo}'")
            print(f"Longitud: {len(codigo)} caracteres")
            print(f"Es numérico: {'Sí' if codigo.isdigit() else 'No'}")
            print("-" * 30)
    
    def ejecutar(self):
        if not self.connection:
            print("No se puede conectar a la base de datos. Saliendo...")
            return
        
        print("Scanner Universal de Bravatec iniciado")
        print("Compatible con cualquier lectora de código de barras")
        time.sleep(2)
        
        try:
            while True:
                modo = self.seleccionar_modo()
                
                if modo is None:
                    break
                elif modo == 'articulos':
                    self.modo_articulos()
                elif modo == 'contenedores':
                    self.modo_contenedores()
                elif modo == 'test':
                    self.modo_test()
                else:
                    print("Modo no implementado aún")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n Saliendo del programa...")
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("Conexión cerrada correctamente")

if __name__ == "__main__":
    app = BravatecScanner()
    app.ejecutar()