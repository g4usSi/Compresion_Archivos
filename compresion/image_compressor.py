import os, pickle
from PIL import Image

def comprimir_imagen(input_path, out_dir):
    img = Image.open(input_path).convert('RGB')
    w,h = img.size
    pixels = list(img.getdata())
    compressed = []

    if not pixels:
        raise ValueError("Imagen vacia")
    prev = pixels[0]; count = 1

    for p in pixels[1:]:
        if p == prev:
            count += 1
        else:
            compressed.append((prev, count))
            prev = p; count = 1

    compressed.append((prev, count))
    basename = os.path.splitext(os.path.basename(input_path))[0]
    out_path = os.path.join(out_dir, basename + ".rle")
    with open(out_path, 'wb') as f:
        pickle.dump((w,h,compressed), f)
    return out_path

def descomprimir_imagen(rle_path, out_dir):
    with open(rle_path, 'rb') as f:
        w,h,compressed = pickle.load(f)
    pixels = []

    for color,count in compressed:
        pixels.extend([color]*count)

    img = Image.new('RGB', (w,h))
    img.putdata(pixels)
    basename = os.path.splitext(os.path.basename(rle_path))[0]
    out_path = os.path.join(out_dir, basename + "_descomprimido.png")
    img.save(out_path)
    return out_path