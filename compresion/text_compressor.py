# Importacion de modulos necesarios
import os, pickle, struct
from collections import Counter
import heapq

# -------------------------------------------------------------
# Clase Node: representa un nodo del arbol de Huffman
# -------------------------------------------------------------
class Node:
    def __init__(self, char=None, freq=0):
        self.char = char       # Caracter almacenado en el nodo (None si es nodo interno)
        self.freq = freq       # Frecuencia de aparicion del caracter
        self.left = None       # Hijo izquierdo
        self.right = None      # Hijo derecho

    # Metodo especial para que los nodos sean comparables en la cola de prioridad
    def __lt__(self, other):
        return self.freq < other.freq

# -------------------------------------------------------------
# Funcion para construir el arbol de Huffman a partir de las frecuencias
# -------------------------------------------------------------
def construir_arbol(freq):
    # Crear una lista de nodos iniciales (uno por caracter)
    heap = [Node(ch, fr) for ch, fr in freq.items()]
    # Convertir la lista en una cola de prioridad (min-heap)
    heapq.heapify(heap)
    
    # Si el texto esta vacio, no hay arbol
    if len(heap) == 0:
        return None

    # Combinar los dos nodos con menor frecuencia hasta que quede uno solo
    while len(heap) > 1:
        a = heapq.heappop(heap)   # Extraer el nodo con menor frecuencia
        b = heapq.heappop(heap)   # Extraer el siguiente menor
        # Crear un nuevo nodo padre con la suma de sus frecuencias
        parent = Node(None, a.freq + b.freq)
        parent.left = a
        parent.right = b
        # Insertar el nodo padre en el heap
        heapq.heappush(heap, parent)

    # El ultimo nodo restante es la raiz del arbol
    return heap[0]


# -------------------------------------------------------------
# Funcion para construir la tabla de codigos Huffman
# -------------------------------------------------------------
def construir_codigo(node, prefix="", table=None):
    if table is None:
        table = {}

    # Caso base: arbol vacio
    if node is None:
        return table

    # Si el nodo es una hoja, asignar el codigo binario actual
    if node.char is not None:
        # Caso especial: si solo hay un caracter, se usa "0" como codigo
        table[node.char] = prefix or "0"
    else:
        # Recorrer rama izquierda (bit 0)
        construir_codigo(node.left, prefix + "0", table)
        # Recorrer rama derecha (bit 1)
        construir_codigo(node.right, prefix + "1", table)

    return table


# -------------------------------------------------------------
# Funcion auxiliar: convertir cadena de bits a bytes
# -------------------------------------------------------------
def bitstring_a_bytes(bitstring):
    # Rellenar con ceros a la izquierda hasta que sea multiplo de 8
    padding = 8 - (len(bitstring) % 8)
    if padding != 8:
        bitstring = bitstring + '0' * padding
    
    # Convertir grupos de 8 bits a bytes
    bytes_list = bytearray()
    for i in range(0, len(bitstring), 8):
        byte = bitstring[i:i+8]
        bytes_list.append(int(byte, 2))
    
    return bytes(bytes_list), padding


# -------------------------------------------------------------
# Funcion auxiliar: convertir bytes a cadena de bits
# -------------------------------------------------------------
def bytes_a_bitstring(data, padding):
    bitstring = ''.join(format(byte, '08b') for byte in data)
    # Remover el padding agregado
    if padding != 8:
        bitstring = bitstring[:-padding]
    return bitstring


# -------------------------------------------------------------
# Funcion para comprimir texto usando Huffman
# -------------------------------------------------------------
def comprimir_texto(txt):
    # Contar la frecuencia de cada caracter
    freq = Counter(txt)
    # Construir el arbol de Huffman
    tree = construir_arbol(freq)
    # Generar la tabla de codigos
    codes = construir_codigo(tree)
    # Reemplazar cada caracter por su codigo binario correspondiente
    bitstring = ''.join(codes[ch] for ch in txt)
    # Convertir a bytes
    data_bytes, padding = bitstring_a_bytes(bitstring)
    # Devolver frecuencias, bytes comprimidos y padding
    return freq, data_bytes, padding


# -------------------------------------------------------------
# Funcion para comprimir un archivo de texto a binario (.bin)
# -------------------------------------------------------------
def comprimir_archivo(input_path, out_dir):
    # Leer el contenido del archivo de texto
    with open(input_path, 'r', encoding='utf-8', errors="ignore") as f:
        text = f.read()

    # Comprimir el texto
    freq, data_bytes, padding = comprimir_texto(text)

    # Crear el nombre del archivo comprimido (.bin)
    basename = os.path.splitext(os.path.basename(input_path))[0]
    out_path = os.path.join(out_dir, basename + ".bin")

    # Guardar las frecuencias, padding y datos comprimidos usando pickle
    with open(out_path, 'wb') as f:
        pickle.dump((freq, padding, data_bytes), f)

    # Devolver la ruta del archivo comprimido
    return out_path


# -------------------------------------------------------------
# Funcion para descomprimir un archivo comprimido (.bin)
# -------------------------------------------------------------
def descomprimir_archivo(bin_path, out_dir):
    # Cargar las frecuencias, padding y bytes desde el archivo
    with open(bin_path, 'rb') as f:
        freq, padding, data_bytes = pickle.load(f)

    # Convertir bytes nuevamente a bitstring
    bitstring = bytes_a_bitstring(data_bytes, padding)

    # Reconstruir el arbol de Huffman a partir de las frecuencias
    tree = construir_arbol(freq)
    # Generar nuevamente la tabla de codigos
    codes = construir_codigo(tree)
    # Crear el diccionario inverso (codigo -> caracter)
    rev = {v: k for k, v in codes.items()}

    # Decodificar el texto bit a bit
    decoded_chars = []
    buffer = ""
    for bit in bitstring:
        buffer += bit
        if buffer in rev:
            decoded_chars.append(rev[buffer])
            buffer = ""

    # Unir los caracteres decodificados en una cadena
    text = ''.join(decoded_chars)

    # Crear el nombre del archivo descomprimido
    basename = os.path.splitext(os.path.basename(bin_path))[0]
    out_path = os.path.join(out_dir, basename + "_descomprimido.txt")

    # Guardar el texto descomprimido en un archivo
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)

    # Devolver la ruta del archivo de salida
    return out_path