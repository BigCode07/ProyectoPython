#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación rápida del sistema
Ejecutar: python3 verificar_sistema.py
"""

import sys
import os

def verificar_modulo(nombre, es_opcional=False):
    """Verifica si un módulo está instalado"""
    try:
        __import__(nombre)
        print(f"  ✓ {nombre:20} → INSTALADO")
        return True
    except ImportError:
        if es_opcional:
            print(f"  ⚠ {nombre:20} → No instalado (opcional)")
        else:
            print(f"  ✗ {nombre:20} → FALTA (requerido)")
        return False

def verificar_archivo(ruta):
    """Verifica si un archivo existe"""
    if os.path.exists(ruta):
        print(f"  ✓ {ruta}")
        return True
    else:
        print(f"  ✗ {ruta} - NO ENCONTRADO")
        return False

def main():
    print("\n" + "="*70)
    print(" VERIFICACIÓN DEL SISTEMA - Bravatec")
    print("="*70)
    
    print(f"\n📍 Python: {sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")
    
    # Verificar módulos requeridos
    print("\n" + "-"*70)
    print(" Módulos Python:")
    print("-"*70)
    
    modulos_requeridos = [
        ('pygame', False),
        ('serial', False),
    ]
    
    modulos_db = [
        ('MySQLdb', True),
        ('mysql.connector', True),
    ]
    
    modulos_opcionales = [
        ('zebra', True),
    ]
    
    todos_ok = True
    for nombre, opcional in modulos_requeridos:
        if not verificar_modulo(nombre, opcional):
            todos_ok = False
    
    print("\n  Base de datos (se necesita al menos uno):")
    db_ok = False
    for nombre, opcional in modulos_db:
        if verificar_modulo(nombre, True):
            db_ok = True
    
    if not db_ok:
        print("\n  ⚠ ADVERTENCIA: No se encontró ningún driver de MySQL")
        print("    Instala uno de estos:")
        print("      pip3 install mysqlclient")
        print("      pip3 install mysql-connector-python")
        todos_ok = False
    
    print("\n  Impresoras:")
    for nombre, opcional in modulos_opcionales:
        verificar_modulo(nombre, True)
    
    # Verificar archivos críticos
    print("\n" + "-"*70)
    print(" Archivos Críticos:")
    print("-"*70)
    
    archivos_criticos = [
        'zebra_compat.py',
        'transitos_a.py',
        'universal_scanner.py',
        'img/logo200x50.png',
        'img/logo600x100.png',
    ]
    
    for archivo in archivos_criticos:
        if not verificar_archivo(archivo):
            todos_ok = False
    
    # Verificar zebra_compat
    print("\n" + "-"*70)
    print(" Módulo de Compatibilidad Zebra:")
    print("-"*70)
    
    try:
        from zebra_compat import Zebra, ZEBRA_DISPONIBLE, verificar_impresoras
        print("  ✓ zebra_compat importado correctamente")
        
        if ZEBRA_DISPONIBLE:
            print("  ✓ Modo: IMPRESIÓN REAL")
        else:
            print("  ⚠ Modo: SIMULACIÓN (sin python-zebra)")
            
    except Exception as e:
        print(f"  ✗ Error al importar zebra_compat: {e}")
        todos_ok = False
    
    # Resumen final
    print("\n" + "="*70)
    if todos_ok:
        print(" ✓✓✓ SISTEMA LISTO PARA USAR ✓✓✓")
    else:
        print(" ⚠ SISTEMA CON ADVERTENCIAS")
        print("\n Revisa los mensajes anteriores e instala los módulos faltantes.")
    print("="*70)
    
    # Instrucciones adicionales
    if not todos_ok:
        print("\n📝 Comandos útiles:")
        print("   pip3 install pygame pyserial mysqlclient")
        print("   pip3 install python-zebra  # Opcional, para impresoras")
    
    print("\n")

if __name__ == "__main__":
    main()

