import os
from PIL import Image

def comprimir_imagen(input_path, out_dir):
    """
    Comprime una imagen usando RLE (Run-Length Encoding) en formato binario puro
    Formato: width(4B) + height(4B) + num_runs(4B) + [R(1B) + G(1B) + B(1B) + count(1B)]*
    """
    img = Image.open(input_path).convert('RGB')
    w, h = img.size
    pixels = list(img.getdata())

    if not pixels:
        raise ValueError("Imagen vacía")

    # Aplicar RLE
    compressed = []
    current_color = pixels[0]
    count = 1

    for pixel in pixels[1:]:
        if pixel == current_color and count < 255:  # Límite 255 por byte
            count += 1
        else:
            compressed.append((current_color, count))
            current_color = pixel
            count = 1
    
    # Agregar la última corrida
    compressed.append((current_color, count))

    # Guardar en formato binario puro
    basename = os.path.splitext(os.path.basename(input_path))[0]
    out_path = os.path.join(out_dir, basename + ".rle")

    with open(out_path, "wb") as f:
        # Header: ancho, alto, número de corridas (12 bytes total)
        f.write(w.to_bytes(4, 'big'))
        f.write(h.to_bytes(4, 'big'))
        f.write(len(compressed).to_bytes(4, 'big'))
        
        # Datos: cada corrida = 4 bytes (R + G + B + count)
        for (r, g, b), count in compressed:
            f.write(bytes([r, g, b, count]))

    return out_path


def descomprimir_imagen(rle_path, out_dir):
    """
    Descomprime una imagen en formato RLE binario
    """
    with open(rle_path, "rb") as f:
        # Leer header (12 bytes)
        w = int.from_bytes(f.read(4), 'big')
        h = int.from_bytes(f.read(4), 'big')
        num_runs = int.from_bytes(f.read(4), 'big')
        
        # Leer corridas
        pixels = []
        for _ in range(num_runs):
            data = f.read(4)  # R, G, B, count
            if len(data) < 4:
                break
            r, g, b, count = data[0], data[1], data[2], data[3]
            pixels.extend([(r, g, b)] * count)

    # Verificar dimensiones
    expected_pixels = w * h
    if len(pixels) != expected_pixels:
        raise ValueError(f"Error: se esperaban {expected_pixels} píxeles, se obtuvieron {len(pixels)}")

    # Crear imagen
    img = Image.new("RGB", (w, h))
    img.putdata(pixels)
    
    basename = os.path.splitext(os.path.basename(rle_path))[0]
    out_path = os.path.join(out_dir, basename + "_descomprimido.png")
    img.save(out_path)
    
    return out_path