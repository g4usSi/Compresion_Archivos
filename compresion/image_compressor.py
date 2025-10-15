import os
from PIL import Image

def comprimir_imagen(path_entrada, direccion_salida):
    img = Image.open(path_entrada).convert('RGB')
    w, h = img.size
    pixeles = list(img.getdata())

    if not pixeles:
        raise ValueError("Imagen vacia")

    # Aplicar RLE
    compressed = []
    colores = pixeles[0]
    count = 1

    for pixel in pixeles[1:]:
        if pixel == colores and count < 255:  # Límite 255 por byte
            count += 1
        else:
            compressed.append((colores, count))
            colores = pixel
            count = 1
    
    # Agregar la ultima corrida
    compressed.append((colores, count))

    # Guardar en formato binario puro
    basename = os.path.splitext(os.path.basename(path_entrada))[0]
    path_salida = os.path.join(direccion_salida, basename + ".rle")

    with open(path_salida, "wb") as f:
        # Header: ancho, alto, número de corridas (12 bytes total)
        f.write(w.to_bytes(4, 'big'))
        f.write(h.to_bytes(4, 'big'))
        f.write(len(compressed).to_bytes(4, 'big'))
        
        # Datos: cada corrida = 4 bytes (R + G + B + count)
        for (r, g, b), count in compressed:
            f.write(bytes([r, g, b, count]))

    return path_salida

def descomprimir_imagen(rle_path, out_dir):
    with open(rle_path, "rb") as f:
        # Leer header (12 bytes)
        w = int.from_bytes(f.read(4), 'big')
        h = int.from_bytes(f.read(4), 'big')
        num_runs = int.from_bytes(f.read(4), 'big')
        
        # Leer corridas
        pixeles = []
        for _ in range(num_runs):
            data = f.read(4)  # R, G, B, contador
            if len(data) < 4:
                break
            r, g, b, count = data[0], data[1], data[2], data[3]
            pixeles.extend([(r, g, b)] * count)

    # Verificar dimensiones
    pixeles_esperados = w * h
    if len(pixeles) != pixeles_esperados:
        raise ValueError(f"Error: se esperaban {pixeles_esperados} pixeles, se obtuvieron {len(pixeles)}")

    # Crear imagen
    img = Image.new("RGB", (w, h))
    img.putdata(pixeles)
    
    nombre_base = os.path.splitext(os.path.basename(rle_path))[0]
    ruta_salida = os.path.join(out_dir, nombre_base + "_descomprimido.png")
    img.save(ruta_salida)
    
    return ruta_salida