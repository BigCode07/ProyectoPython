# Sistema Bravatec - Gestión de Códigos de Barras

Sistema universal de lectura de códigos de barras compatible con cualquier lectora y entrada manual por teclado.

## 📦 Instalación en Raspberry Pi

### Requisitos Previos
- Raspberry Pi con Raspbian/Raspberry Pi OS
- Python 2.7 o Python 3.x
- Conexión a red (para base de datos)
- Impresora Zebra conectada

### Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Python y pip
sudo apt-get install python-pip python-dev -y

# Instalar librería MySQL (opción recomendada para Raspberry Pi)
sudo apt-get install python-mysqldb -y

# Alternativa: Si MySQLdb no funciona, instalar mysql-connector
pip install mysql-connector-python

# Instalar otras dependencias
pip install pygame
pip install pyserial
pip install zebra

# O instalar todas desde requirements.txt (si existe)
pip install -r requirements.txt
```

### Verificar Instalación de MySQL

```bash
# Probar conexión MySQL
python -c "import MySQLdb; print('MySQLdb OK')"

# Si falla, probar mysql.connector
python -c "import mysql.connector; print('mysql.connector OK')"
```

### Configuración

Los scripts están configurados para **detectar automáticamente** la librería MySQL disponible:
- Primero intenta usar `MySQLdb` (nativa de Raspberry Pi)
- Si no está disponible, usa `mysql.connector`

**Configuración de Base de Datos** (ya incluida en los scripts):
```python
DB_CONFIG = {
    'host': '192.168.11.3',
    'port': 3306,
    'user': 'root',
    'password': 'bravatec',
    'database': 'bravatec'
}
```

### Ejecución de Programas

```bash
# Programa principal universal
python universal_scanner.py

# Programa de tránsitos
python transitos_a.py

# Programa de contenedores
python contenedor_upc.py

# Programa de headsets
python hts_a.py
python hts_upc.py

# Reimpresión de etiquetas
python reimpresion_upc.py
```

---

## 🔧 Solución de Problemas

### Error: "No module named mysql.connector" o "No module named MySQLdb"

**Opción 1: Instalar MySQLdb (Recomendado para Raspberry Pi)**
```bash
sudo apt-get install python-mysqldb python3-mysqldb -y
```

**Opción 2: Instalar mysql-connector-python**
```bash
pip install mysql-connector-python
# O para Python 3
pip3 install mysql-connector-python
```

**Opción 3: Compilar MySQLdb desde source**
```bash
sudo apt-get install libmysqlclient-dev -y
pip install mysqlclient
```

### Error: "No se pudo conectar a la base de datos"
```bash
# Verificar conectividad
ping 192.168.11.3

# Verificar puerto MySQL
telnet 192.168.11.3 3306
```

### Error: Impresora no responde
```bash
# Listar impresoras
lpstat -p -d

# Verificar Zebra
lsusb | grep Zebra
```

---


```python
# En universal_scanner.py
self.impresora_grande = 'Zebra_1'  # Para etiquetas 80x40mm
self.impresora_chica = 'Zebra_0'   # Para etiquetas 38x20mm
```

### Inicio Rápido
```bash
# Ejecutar el programa
python universal_scanner.py

# Seleccionar modo desde el menú
# Escanear o escribir códigos
# ¡Listo!
```

### Flujo de Trabajo
1. **Iniciar programa** → Menú principal
2. **Seleccionar modo** → Artículos/Contenedores/Test
3. **Escanear/Escribir** → El sistema detecta automáticamente
4. **Confirmar** → Etiqueta se imprime automáticamente


### Algoritmo de Detección
```python
# Parámetros de detección
scanner_speed_threshold = 0.1  # 100ms entre caracteres

# Lógica
if tiempo_entre_caracteres < 100ms:
    → SCANNER (entrada rápida)
else:
    → MANUAL (entrada humana)
```


#### 3. Test de Impresora
```python
from zebra import Zebra
z = Zebra('Zebra_0')
z.output('^XA^FO50,50^FDTest^FS^XZ')
```

### Códigos de Error

| Error | Descripción | Acción |
|-------|-------------|---------|
| `DB001` | Conexión fallida | Verificar red |
| `SC001` | Scanner no responde | Reconectar USB |
| `PR001` | Impresora offline | Encender impresora |
| `CD001` | Código inválido | Verificar formato |

## 📁 Estructura del Proyecto

```
scanner-universal/
├── universal_scanner.py      # Programa principal
├── requirements.txt          # Dependencias Python
├── README.md                # Este archivo
├── config/
│   ├── database.conf        # Configuración de BD
│   └── printers.conf        # Configuración impresoras
├── img/
│   ├── logo200x50.png       # Logo Bravatec
│   └── logo600x100.png      # Logo grande
├── templates/
│   ├── articulo.zpl         # Plantilla etiqueta artículo
│   ├── contenedor.zpl       # Plantilla etiqueta contenedor
│   └── headset.zpl          # Plantilla etiqueta headset
└── legacy/
    ├── reimpresion_upc.py   # Versión original artículos
    ├── transitos_a.py       # Versión original tránsitos
    ├── hts_upc.py          # Versión original headsets
    ├── hts_a.py            # Versión original HTS avanzado
    ├── contenedor_upc.py   # Versión original contenedores
    ├── comandos_upc.py     # Versión original comandos 1
    └── comandos2_upc.py    # Versión original comandos 2
```

