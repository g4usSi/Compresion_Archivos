import os, pickle, wave, struct

# Funcion para leer un archivo WAV y obtener sus muestras
def leer_wav_sample(path):
    with wave.open(path, 'rb') as wf:
        params = wf.getparams()
        n = wf.getnframes()
        frames = wf.readframes(n)
        fmt = '<' + 'h' * (n * params.nchannels)
        samples = list(struct.unpack(fmt, frames))
    return params, samples

# Funcion para escribir un archivo WAV a partir de una lista de muestras
def escribir_wav_samples(path, params, samples):
    with wave.open(path, 'wb') as wf:
        wf.setparams(params)
        frames = struct.pack('<' + 'h' * len(samples), *samples)
        wf.writeframes(frames)

# Funcion para comprimir un archivo WAV usando cuantizacion y RLE
def comprimir_wav(wav_entrada, out_dir, quant=500):
    params, samples = leer_wav_sample(wav_entrada)
    q = [int(s / quant) * quant for s in samples]
    comprimido = []
    prev = q[0]
    count = 1
    for s in q[1:]:
        if s == prev:
            count += 1
        else:
            comprimido.append((prev, count))
            prev = s
            count = 1
    comprimido.append((prev, count))
    basename = os.path.splitext(os.path.basename(wav_entrada))[0]
    out_path = os.path.join(out_dir, basename + ".arle")
    with open(out_path, 'wb') as f:
        pickle.dump((params, comprimido), f)
    stats = {
        "samples": len(samples),
        "runs": len(comprimido),
        "quant": quant
    }
    return out_path, stats

# Funcion para descomprimir un archivo .arle y reconstruir el WAV
def descomprimir_wav(arle_path, out_dir):
    with open(arle_path, 'rb') as f:
        params, comprimido = pickle.load(f)
    samples = []
    for val, count in comprimido:
        samples.extend([val] * count)
    basename = os.path.splitext(os.path.basename(arle_path))[0]
    out_path = os.path.join(out_dir, basename + "_recon.wav")
    escribir_wav_samples(out_path, params, samples)
    return out_path