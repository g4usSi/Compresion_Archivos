# CompresorDeDatos (PyQt5)
Proyecto educativo: compresión de texto (Huffman), imágenes (RLE) y audio (RLE adaptado).
Estructura lista para que cada integrante trabaje en su módulo.

## Requisitos
- Python 3.8+
- PyQt5
- Pillow

Instalación (recomendado):
```
python -m pip install PyQt5 Pillow
```

## Ejecutar
```
python main.py
```

## Notas
- El Huffman implementado es educativo: almacena la tabla de frecuencias y el bitstring con `pickle`.
- El RLE de imágenes funciona mejor con imágenes de pocos colores.
- El RLE de audio quantiza muestras antes de aplicar RLE.

