import os
import time
from zebra_compat import Zebra  # Módulo compatible con o sin python-zebra

class Articulo:
    def __init__(self):
        self.titulo = 'Bravatec reimpresion etiquetas\n'
        self.impresora = 'Zebra_0'

    def ingresar_comando(self):
        os.system('clear')
        print(self.titulo)
        idarticulo = input('Cod: ')
        if idarticulo == '':
            print('Cod no valido')
            time.sleep(1)
            return False
        elif idarticulo == '0':
            exit()
        else:
            return idarticulo

    def imprimir(self, idarticulo):
        codigo = idarticulo
        etiqueta = """^XA
^CF0,34
^FWB
^FO280,20^FDNUEVE^FS
^BY2
^BUN,120,Y,N,N
^FO350,20
^FD%s^FS
^XZ""" % codigo
        z = Zebra(self.impresora)
        z.output(etiqueta)

articulo = Articulo()

while True:
    idarticulo = articulo.ingresar_comando()
    if idarticulo:
        articulo.imprimir(idarticulo)
