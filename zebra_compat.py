# -*- coding: utf-8 -*-
"""
Módulo de compatibilidad para impresoras Zebra
Funciona con o sin la librería python-zebra instalada

Uso:
    from zebra_compat import Zebra
    
    z = Zebra('Zebra_0')
    z.output(etiqueta_zpl)
"""

import os
import sys
from datetime import datetime

# Intentar importar la librería real de zebra
try:
    from zebra import Zebra as ZebraReal
    ZEBRA_DISPONIBLE = True
    print("✓ Librería zebra disponible - modo impresión real")
except ImportError:
    ZEBRA_DISPONIBLE = False
    print("⚠ Librería zebra no disponible - modo simulación")
    print("  Para instalar: pip3 install python-zebra")


class ZebraMock:
    """Clase mock para simular la impresora Zebra cuando no está disponible"""
    
    def __init__(self, nombre_impresora='Zebra_0'):
        self.nombre_impresora = nombre_impresora
        self.contador = 0
        
        # Crear directorio para guardar las etiquetas simuladas
        self.directorio_etiquetas = 'etiquetas_simuladas'
        if not os.path.exists(self.directorio_etiquetas):
            try:
                os.makedirs(self.directorio_etiquetas)
                print(f"  Directorio creado: {self.directorio_etiquetas}/")
            except:
                pass
    
    def output(self, etiqueta):
        """Simula la impresión de una etiqueta"""
        self.contador += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"{self.directorio_etiquetas}/etiqueta_{timestamp}_{self.contador}.zpl"
        
        # Guardar la etiqueta en un archivo
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write(etiqueta)
            print(f"  [SIMULADO] Etiqueta guardada en: {nombre_archivo}")
        except Exception as e:
            print(f"  [SIMULADO] No se pudo guardar etiqueta: {e}")
        
        # Mostrar información en consola
        self._mostrar_info_etiqueta(etiqueta)
    
    def _mostrar_info_etiqueta(self, etiqueta):
        """Extrae y muestra información básica de la etiqueta ZPL"""
        try:
            # Intentar extraer códigos de barras
            if '^FD' in etiqueta:
                lineas = etiqueta.split('^FD')
                print(f"  [SIMULADO] Impresora: {self.nombre_impresora}")
                print(f"  [SIMULADO] Contenido detectado:")
                for linea in lineas[1:]:
                    contenido = linea.split('^')[0].strip()
                    if contenido and len(contenido) < 50:  # Solo mostrar textos cortos
                        print(f"    - {contenido}")
        except:
            pass


class Zebra:
    """
    Wrapper universal para impresoras Zebra
    Usa la librería real si está disponible, sino simula la impresión
    """
    
    def __init__(self, nombre_impresora='Zebra_0'):
        self.nombre_impresora = nombre_impresora
        
        if ZEBRA_DISPONIBLE:
            try:
                self._printer = ZebraReal(nombre_impresora)
            except Exception as e:
                print(f"⚠ Error al conectar impresora real, usando modo simulación: {e}")
                self._printer = ZebraMock(nombre_impresora)
        else:
            self._printer = ZebraMock(nombre_impresora)
    
    def output(self, etiqueta):
        """Envía una etiqueta ZPL a la impresora (real o simulada)"""
        try:
            self._printer.output(etiqueta)
        except Exception as e:
            print(f"✗ Error al imprimir/simular: {e}")
            raise


# Función de utilidad para verificar si las impresoras están disponibles
def verificar_impresoras():
    """Verifica el estado de las impresoras Zebra"""
    print("\n" + "="*60)
    print("  VERIFICACIÓN DE IMPRESORAS ZEBRA")
    print("="*60)
    
    if ZEBRA_DISPONIBLE:
        print("✓ Librería python-zebra: INSTALADA")
        try:
            from zebra import Zebra as ZebraReal
            # Intentar listar impresoras
            print("  Intentando conectar con impresoras...")
            for nombre in ['Zebra_0', 'Zebra_1']:
                try:
                    z = ZebraReal(nombre)
                    print(f"  ✓ {nombre}: DISPONIBLE")
                except Exception as e:
                    print(f"  ✗ {nombre}: NO DISPONIBLE ({e})")
        except Exception as e:
            print(f"  ⚠ Error al verificar impresoras: {e}")
    else:
        print("✗ Librería python-zebra: NO INSTALADA")
        print("\n  Para instalar:")
        print("    pip3 install python-zebra")
        print("    # o")
        print("    pip3 install git+https://github.com/belono/python-zebra.git")
        print("\n  Mientras tanto, se usará el modo simulación")
        print("  Las etiquetas se guardarán en: etiquetas_simuladas/")
    
    print("="*60 + "\n")


# Auto-verificación al importar el módulo
if __name__ == "__main__":
    verificar_impresoras()
    
    # Test de ejemplo
    print("\nPrueba de impresión:")
    z = Zebra('Zebra_0')
    etiqueta_test = """^XA
^CF0,60
^FO50,50^FDTest Bravatec^FS
^BY2
^BUN,100,Y,N,N
^FO50,150^FD12345678901^FS
^XZ"""
    z.output(etiqueta_test)
    print("\n✓ Prueba completada")

