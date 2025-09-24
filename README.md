

Sistema universal de lectura de códigos de barras compatible con cualquier lectora y entrada manual por teclado.


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

