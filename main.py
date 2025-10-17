import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTextEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QProgressBar
from PyQt5.QtCore import Qt
from compresion import text_compressor, image_compressor, audio_compressor
from PyQt5.QtGui import QFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
fuente = QFont("Century Gothic", 12) 

#TEXTO
class TextoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.info = QLabel("Selecciona un archivo .txt")
        self.info.setFixedHeight(100)
        self.info.setAlignment(Qt.AlignCenter)
    
        self.info.setFont(fuente)

        layout.addWidget(self.info)
        btns = QHBoxLayout()
        self.cargar_btn = QPushButton("Cargar .txt")
        self.comprimir_btn = QPushButton("Comprimir (Huffman)")
        self.descomprimir_btn = QPushButton("Descomprimir .bin")
        for btn in [self.cargar_btn, self.comprimir_btn, self.descomprimir_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(fuente)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2f3136;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #fc5e5b; }
                QPushButton:pressed { background: #fc5e5b; }
            """)
        btns.addWidget(self.cargar_btn); btns.addWidget(self.comprimir_btn); btns.addWidget(self.descomprimir_btn)
        layout.addLayout(btns)
        self.resultado = QTextEdit(); self.resultado.setReadOnly(True); layout.addWidget(self.resultado)
        self.setLayout(layout)

        self.filepath = None
        self.cargar_btn.clicked.connect(self.cargar_archivo)
        self.comprimir_btn.clicked.connect(self.comprimir)
        self.descomprimir_btn.clicked.connect(self.decompress)

    def cargar_archivo(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar txt", "", "Text files (*.txt)")
        if fn:
            self.filepath = fn
            self.info.setText(f"Archivo: {fn}")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero un .txt")
            return

        # Ejecutar la compresion
        out = text_compressor.comprimir_archivo(self.filepath, OUT_DIR)
        orig = os.path.getsize(self.filepath)
        comp = os.path.getsize(out)

        # 🔹 Leer el archivo comprimido (.bin) para obtener los datos comprimidos
        import pickle
        with open(out, 'rb') as f:
            freq, padding, data_bytes = pickle.load(f)

        # Calcular estadísticas
        total_bits = len(data_bytes) * 8 - padding  # bits reales sin padding
        tamano_real_comprimido = len(data_bytes)  # tamaño en bytes del binario puro
        porcentaje_compresion = (1 - (tamano_real_comprimido / orig)) * 100 if orig != 0 else 0

        # Contar frecuencias para estadisticas
        total_caracteres = sum(freq.values())

        # Mostrar resultados
        self.resultado.setPlainText(
            f"Comprimido: {out}\n"
            f"Tamaño original: {orig} bytes\n"
            f"Tamaño comprimido (binario puro): {tamano_real_comprimido} bytes\n"
            f"Tamaño archivo .bin (con metadatos): {comp} bytes\n"
            f"Compresión lograda: {porcentaje_compresion:.2f}%\n\n"
            f"--- Estadísticas de codificación ---\n"
            f"Total de caracteres: {total_caracteres}\n"
            f"Total de bits utilizados: {total_bits}\n"
            f"Caracteres únicos: {len(freq)}\n"
            f"Padding agregado: {padding} bits\n"
        )

    def decompress(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .bin (Huffman)", "", "Binary files (*.bin);;All files (*)")
        if not fn:
            return
        out = text_compressor.descomprimir_archivo(fn, OUT_DIR)
        QMessageBox.information(self, "Hecho", f"Archivo descomprimido: {out}")

# IMAGEN
class ImagenTab(QWidget):
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.info = QLabel("Selecciona una imagen (.png/.bmp)")
        self.info.setFixedHeight(100)
        self.info.setAlignment(Qt.AlignCenter)
    
        self.info.setFont(fuente)
        layout.addWidget(self.info)

        btns = QHBoxLayout()
        self.load_btn = QPushButton("Cargar imagen")
        self.compress_btn = QPushButton("Comprimir (RLE)")
        self.decompress_btn = QPushButton("Descomprimir .rle")
        for btn in [self.load_btn, self.compress_btn, self.decompress_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(fuente)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2f3136;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #fc5e5b; }
                QPushButton:pressed { background: #fc5e5b; }
            """)
        btns.addWidget(self.load_btn)
        btns.addWidget(self.compress_btn)
        btns.addWidget(self.decompress_btn)
        layout.addLayout(btns)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)

        self.filepath = None
        self.load_btn.clicked.connect(self.cargar_archivo)
        self.compress_btn.clicked.connect(self.comprimir)
        self.decompress_btn.clicked.connect(self.descomprimir)

    def cargar_archivo(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.bmp *.jpg)")
        if fn:
            self.filepath = fn
            # Detectar tipo de archivo
            ext = os.path.splitext(fn)[1].lower()
            if ext == '.bmp':
                self.info.setText(f"✅ Imagen BMP: {fn}\n(RLE funciona muy bien con BMP)")
            elif ext in ['.png', '.jpg', '.jpeg']:
                self.info.setText(f"⚠️ Imagen comprimida: {fn}\n(RLE puede NO reducir el tamaño)")
            else:
                self.info.setText(f"Imagen: {fn}")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero una imagen")
            return

        try:
            # Ejecutar compresión
            out = image_compressor.comprimir_imagen(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)

            # Leer el archivo binario RLE para extraer estadísticas
            with open(out, "rb") as f:
                # Leer header (12 bytes)
                w = int.from_bytes(f.read(4), 'big')
                h = int.from_bytes(f.read(4), 'big')
                num_runs = int.from_bytes(f.read(4), 'big')
                
                # Leer corridas y extraer colores únicos
                unique_colors = set()
                for _ in range(num_runs):
                    data = f.read(4)  # R, G, B, count
                    if len(data) < 4:
                        break
                    r, g, b, count = data[0], data[1], data[2], data[3]
                    unique_colors.add((r, g, b))

            # Estadísticas RLE
            total_pixels = w * h
            runs = num_runs
            promedio_corrida = total_pixels / runs if runs != 0 else 0
            porcentaje_compresion = (1 - (comp / orig)) * 100 if orig != 0 else 0

            # Calcular overhead y datos reales
            header_size = 12  # bytes
            data_size = runs * 4  # bytes (cada corrida = 4 bytes)
            total_calculado = header_size + data_size
            
            # Determinar tipo de archivo original
            ext = os.path.splitext(self.filepath)[1].lower()
            formato_original = "BMP (sin comprimir)" if ext == '.bmp' else f"{ext.upper()} (comprimido)"
            
            # Advertencia si compresión es negativa
            advertencia = ""
            if porcentaje_compresion < 0:
                advertencia = ("\n⚠️ ADVERTENCIA: El archivo creció.\n"
                              "RLE funciona mejor con archivos BMP sin comprimir\n"
                              "o imágenes más grandes con áreas uniformes.")
            
            # Calcular eficiencia de RLE
            bytes_sin_comprimir = total_pixels * 3  # RGB sin comprimir
            ratio_vs_raw = (1 - (comp / bytes_sin_comprimir)) * 100
            
            # Mostrar resultados
            self.result.setPlainText(
                f"Comprimido: {out}\n"
                f"Formato original: {formato_original}\n"
                f"Tamaño original: {orig:,} bytes\n"
                f"Tamaño comprimido: {comp:,} bytes\n"
                f"Compresión real: {porcentaje_compresion:.2f}%{advertencia}\n\n"
                f"--- Estadísticas RLE (Imagen) ---\n"
                f"Dimensiones: {w} x {h} = {total_pixels:,} píxeles\n"
                f"Corridas detectadas: {runs:,}\n"
                f"Promedio de longitud por corrida: {promedio_corrida:.2f} píxeles\n"
                f"Colores únicos en corridas: {len(unique_colors):,}\n\n"
                f"--- Desglose del archivo RLE ---\n"
                f"Header (metadatos): {header_size} bytes\n"
                f"Datos RLE: {data_size:,} bytes ({runs:,} corridas × 4 bytes)\n"
                f"Total calculado: {total_calculado:,} bytes\n"
                f"Archivo real: {comp:,} bytes\n"
                f"Overhead del header: {((header_size / comp) * 100):.4f}%\n\n"
                f"--- Comparación con datos sin comprimir ---\n"
                f"Tamaño raw (RGB): {bytes_sin_comprimir:,} bytes\n"
                f"Compresión vs raw: {ratio_vs_raw:.2f}%"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al comprimir", f"Ocurrió un error:\n{e}")

    def descomprimir(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .rle", "", "RLE files (*.rle);;All files (*)")
        if not fn:
            return
        try:
            out = image_compressor.descomprimir_imagen(fn, OUT_DIR)
            QMessageBox.information(self, "Hecho", f"Imagen reconstruida: {out}")
        except Exception as e:
            QMessageBox.critical(self, "Error al descomprimir", f"Ocurrió un error:\n{e}")
            
# AUDIO
class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.info = QLabel("Selecciona un audio .wav (16-bit PCM preferible)")
        self.info.setFixedHeight(100)
        self.info.setAlignment(Qt.AlignCenter)
    
        self.info.setFont(fuente)
        layout.addWidget(self.info)

        btns = QHBoxLayout()
        self.load_btn = QPushButton("Cargar .wav")
        self.compress_btn = QPushButton("Comprimir (RLE adaptado)")
        self.decompress_btn = QPushButton("Descomprimir .arle")
        for btn in [self.load_btn, self.compress_btn, self.decompress_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(fuente)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2f3136;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #fc5e5b; }
                QPushButton:pressed { background: #fc5e5b; }
            """)
        btns.addWidget(self.load_btn)
        btns.addWidget(self.compress_btn)
        btns.addWidget(self.decompress_btn)
        layout.addLayout(btns)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)

        self.filepath = None
        self.load_btn.clicked.connect(self.cargar_archivo)
        self.compress_btn.clicked.connect(self.comprimir)
        self.decompress_btn.clicked.connect(self.descomprimir)

    def cargar_archivo(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar wav", "", "WAV files (*.wav)")
        if fn:
            self.filepath = fn
            self.info.setText(f"Audio: {fn}")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero un .wav")
            return

        try:
            out, stats = audio_compressor.comprimir_wav(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)

            import pickle
            with open(out, 'rb') as f:
                params, compressed = pickle.load(f)
                # params = (nchannels, sampwidth, framerate, nframes, comptype, compname)
                nch, sampwidth, fr, nframes, *_ = params

            # Calcular estadísticas RLE adaptado
            total_muestras = nframes * nch
            corridas = len(compressed)
            promedio_corrida = total_muestras / corridas if corridas != 0 else 0
            porcentaje_compresion = (1 - (comp / orig)) * 100 if orig != 0 else 0

            self.result.setPlainText(
                f"Comprimido: {out}\n"
                f"Tamaño original: {orig} bytes\n"
                f"Tamaño comprimido: {comp} bytes\n"
                f"Compresión real: {porcentaje_compresion:.2f}%\n\n"
                f"--- Estadísticas RLE (Audio) ---\n"
                f"Canales: {nch}\n"
                f"Profundidad de bits: {sampwidth * 8}\n"
                f"Muestras totales: {total_muestras}\n"
                f"Corridas detectadas: {corridas}\n"
                f"Promedio de longitud por corrida: {promedio_corrida:.2f} muestras\n"
                f"Frecuencia de muestreo: {fr} Hz\n\n"
                f"Notas del compresor:\n{stats}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al comprimir", f"Ocurrió un error:\n{e}")

    def descomprimir(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .arle", "", "Audio-RLE files (*.arle);;All files (*)")
        if not fn:
            return
        try:
            out = audio_compressor.descomprimir_wav(fn, OUT_DIR)
            QMessageBox.information(self, "Hecho", f"Audio reconstruido: {out}")
        except Exception as e:
            QMessageBox.critical(self, "Error al descomprimir", f"Ocurrió un error:\n{e}")


#VENTANA PRINCIPAL
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compresor de Datos - PyQt5")
        self.setStyleSheet("""
            QMainWindow {
                background: #F0F0F0;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #F0F0F0;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #F0F0F0;
                border-bottom: 3px solid #fc5e5b;
            }
            QTabBar::tab:hover {
                background: #e8e8e8;
            }
        """)
        tabs = QTabWidget()
        tabs.setFont(fuente)
        tabs.addTab(TextoTab(), "Texto (Huffman)")
        tabs.addTab(ImagenTab(), "Imagen (RLE)")
        tabs.addTab(AudioTab(), "Audio (RLE adaptado)")
        self.setCentralWidget(tabs)
        self.resize(800, 600)

def main():
    app = QApplication(sys.argv)
    w = VentanaPrincipal()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
