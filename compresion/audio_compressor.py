# Importacion de modulos necesarios
import os, pickle, wave, struct

# -------------------------------------------------------------
# Funcion para leer un archivo WAV y obtener sus muestras
# -------------------------------------------------------------
def leer_wav_sample(path):
    # Abrir el archivo WAV en modo lectura binaria
    with wave.open(path, 'rb') as wf:
        # Obtener los parametros del archivo (frecuencia, canales, etc.)
        params = wf.getparams()
        # Numero total de cuadros (frames) en el archivo
        n = wf.getnframes()
        # Leer todos los cuadros del archivo
        frames = wf.readframes(n)
        # Formato de desempaquetado: little-endian ('<') y entero corto ('h')
        fmt = '<' + 'h' * (n * params.nchannels)
        # Convertir los bytes leidos a una lista de numeros enteros (muestras)
        samples = list(struct.unpack(fmt, frames))
    # Devolver los parametros y las muestras
    return params, samples


# -------------------------------------------------------------
# Funcion para escribir un archivo WAV a partir de una lista de muestras
# -------------------------------------------------------------
def escribir_wav_samples(path, params, samples):
    # Abrir un nuevo archivo WAV en modo escritura binaria
    with wave.open(path, 'wb') as wf:
        # Establecer los mismos parametros que tenia el archivo original
        wf.setparams(params)
        # Empaquetar las muestras (lista de enteros) en bytes
        frames = struct.pack('<' + 'h' * len(samples), *samples)
        # Escribir los datos en el nuevo archivo WAV
        wf.writeframes(frames)


# -------------------------------------------------------------
# Funcion para comprimir un archivo WAV usando cuantizacion y RLE
# -------------------------------------------------------------
def comprimir_wav(wav_entrada, out_dir, quant=500):
    # Leer las muestras del archivo WAV original
    params, samples = leer_wav_sample(wav_entrada)

    # Cuantizacion: reducir la precision de las muestras
    # Se divide cada muestra entre el valor 'quant' y se redondea hacia abajo
    # Luego se multiplica de nuevo por 'quant' para limitar los posibles valores
    q = [int(s / quant) * quant for s in samples]

    # Aplicar codificacion por corridas (Run-Length Encoding, RLE)
    comprimido = []
    prev = q[0]
    count = 1
    for s in q[1:]:
        if s == prev:
            # Si la muestra es igual a la anterior, incrementar el contador
            count += 1
        else:
            # Si cambia el valor, guardar la corrida anterior (valor, cantidad)
            comprimido.append((prev, count))
            prev = s
            count = 1
    # Agregar la ultima corrida
    comprimido.append((prev, count))

    # Crear el nombre del archivo comprimido (.arle)
    basename = os.path.splitext(os.path.basename(wav_entrada))[0]
    out_path = os.path.join(out_dir, basename + ".arle")

    # Guardar los datos comprimidos en un archivo binario usando pickle
    with open(out_path, 'wb') as f:
        pickle.dump((params, comprimido), f)

    # Crear estadisticas basicas de la compresion
    stats = {
        "samples": len(samples),
        "runs": len(comprimido),
        "quant": quant
    }

    # Devolver la ruta del archivo comprimido y las estadisticas
    return out_path, stats


# -------------------------------------------------------------
# Funcion para descomprimir un archivo .arle y reconstruir el WAV
# -------------------------------------------------------------
def descomprimir_wav(arle_path, out_dir):
    # Abrir el archivo comprimido y cargar los datos
    with open(arle_path, 'rb') as f:
        params, comprimido = pickle.load(f)

    # Reconstruir la lista de muestras expandiendo las corridas
    samples = []
    for val, count in comprimido:
        samples.extend([val] * count)

    # Crear el nombre del archivo WAV reconstruido
    basename = os.path.splitext(os.path.basename(arle_path))[0]
    out_path = os.path.join(out_dir, basename + "_recon.wav")

    # Escribir las muestras reconstruidas en un nuevo archivo WAV
    escribir_wav_samples(out_path, params, samples)

    # Devolver la ruta del archivo descomprimido
    return out_path