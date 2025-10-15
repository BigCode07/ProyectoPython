# -*- coding: utf-8 -*-
# comandos_upc_corrected.py
import os
import time
from zebra_compat import Zebra

class Articulo:
    def __init__(self):
        self.titulo = 'Bravatec Reimpresion de Etiquetas\n'
        self.impresora = 'Zebra_0'
        # This text was the only difference between the two original files.
        # Make it a configurable attribute.
        self.texto_etiqueta = 'GASTON' # Or 'NUEVE', or load from a config

    def clear_screen(self):
        """Clears the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def ingresar_comando(self):
        self.clear_screen()
        print(self.titulo)
        idarticulo = input('Cod (0 to exit): ')
        if idarticulo == '0':
            exit()
        if not idarticulo.strip():
            print('Codigo no valido')
            time.sleep(1)
            return False
        return idarticulo

    def imprimir(self, idarticulo):
        etiqueta = f"""^XA
^CF0,34
^FWN
^FO350,20^FD{self.texto_etiqueta}^FS
^BY2
^BUN,80,Y,N,N
^FO350,50
^FD{idarticulo}^FS
^XZ"""
        try:
            z = Zebra(self.impresora)
            z.output(etiqueta)
            print(f"Etiqueta para {idarticulo} enviada.")
        except Exception as e:
            print(f"Error al imprimir: {e}")


if __name__ == "__main__":
    articulo = Articulo()
    while True:
        idarticulo = articulo.ingresar_comando()
        if idarticulo:
            articulo.imprimir(idarticulo)
            time.sleep(1) # Pause to show confirmation message