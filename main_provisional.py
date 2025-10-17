import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

# ====== IMPORTA TUS MÓDULOS ======
from compresion import text_compressor, image_compressor, audio_compressor

OUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ====== FUNCIONES AUXILIARES ======
def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_compression_ratio(original, compressed):
    if original == 0:
        return 0
    return ((original - compressed) / original) * 100

# ====== VISTAS ======
class TextoView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        label = QLabel("Compresión de Texto (Huffman)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #A5EFFF; font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        # Botones
        self.load_btn = QPushButton("Cargar Archivo")
        self.comp_btn = QPushButton("Comprimir")
        self.decomp_btn = QPushButton("Descomprimir")
        for b in (self.load_btn, self.comp_btn, self.decomp_btn):
            b.setMinimumHeight(50)
            b.setStyleSheet("""
                QPushButton {
                    background-color: #00B8D9;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                }
                QPushButton:hover { background-color: #00A3C4; }
                QPushButton:pressed { background-color: #008EA8; }
            """)
            layout.addWidget(b)

        # Área de resultados
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("""
            QTextEdit {
                background: #2B2B2B;
                color: #CFCFCF;
                border: 1px solid #3E3E3E;
                border-radius: 10px;
                padding: 12px;
                font-family: Consolas;
                font-size: 15px;
            }
        """)
        layout.addWidget(self.result)

        self.filepath = None
        self.load_btn.clicked.connect(self.load_file)
        self.comp_btn.clicked.connect(self.compress)
        self.decomp_btn.clicked.connect(self.decompress)

    def load_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar txt", "", "Text files (*.txt)")
        if fn:
            self.filepath = fn
            name = os.path.basename(fn)
            size = format_size(os.path.getsize(fn))
            self.result.setPlainText(f"{name} ({size})")

    def compress(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero un archivo .txt")
            return
        try:
            out = text_compressor.comprimir_archivo(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)

            import pickle
            with open(out, 'rb') as f:
                freq, bits = pickle.load(f)

            total_bits = len(bits)
            tamano_teorico_bytes = total_bits / 8
            porcentaje_compresion = (1 - (tamano_teorico_bytes / orig)) * 100 if orig != 0 else 0

            self.result.setPlainText(
                f"Archivo Original: {os.path.basename(self.filepath)} ({orig} bytes)\n"
                f"Archivo Comprimido (pickle): {comp} bytes\n"
                f"Tamaño teórico (empaquetado): {tamano_teorico_bytes:.2f} bytes\n"
                f"Compresión teórica: {porcentaje_compresion:.2f}%\n"
                f"Ruta del archivo comprimido: {out}\n"
                f"Total bits simulados: {total_bits}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def decompress(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .bin (Huffman)", "", "Binary files (*.bin)")
        if fn:
            try:
                out = text_compressor.descomprimir_archivo(fn, OUT_DIR)
                QMessageBox.information(self, "Listo", f"Archivo descomprimido:\n{out}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))



class ImagenView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        label = QLabel("Compresión de Imagen (RLE)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #A5EFFF; font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        # Botones
        self.load_btn = QPushButton("Cargar Imagen")
        self.comp_btn = QPushButton("Comprimir")
        self.decomp_btn = QPushButton("Descomprimir")
        for b in (self.load_btn, self.comp_btn, self.decomp_btn):
            b.setMinimumHeight(50)
            b.setStyleSheet("""
                QPushButton {
                    background-color: #00B8D9;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                }
                QPushButton:hover { background-color: #00A3C4; }
                QPushButton:pressed { background-color: #008EA8; }
            """)
            layout.addWidget(b)

        # Área de resultados
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("""
            QTextEdit {
                background: #2B2B2B;
                color: #CFCFCF;
                border: 1px solid #3E3E3E;
                border-radius: 10px;
                padding: 12px;
                font-family: Consolas;
                font-size: 15px;
            }
        """)
        layout.addWidget(self.result)

        self.filepath = None
        self.load_btn.clicked.connect(self.load_file)
        self.comp_btn.clicked.connect(self.compress)
        self.decomp_btn.clicked.connect(self.decompress)

    def load_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.jpg *.bmp)")
        if fn:
            self.filepath = fn
            size = format_size(os.path.getsize(fn))
            self.result.setPlainText(f"{os.path.basename(fn)} ({size})")

    def compress(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero una imagen")
            return
        try:
            out = image_compressor.comprimir_imagen(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)

            with open(out, "rb") as f:
                w = int.from_bytes(f.read(4), 'big')
                h = int.from_bytes(f.read(4), 'big')
                num_runs = int.from_bytes(f.read(4), 'big')
                unique_colors = set()
                for _ in range(num_runs):
                    data = f.read(4)
                    if len(data) < 4: break
                    r, g, b, count = data[0], data[1], data[2], data[3]
                    unique_colors.add((r, g, b))

            total_pixels = w * h
            runs = num_runs
            promedio_corrida = total_pixels / runs if runs != 0 else 0
            porcentaje_compresion = (1 - (comp / orig)) * 100 if orig != 0 else 0

            self.result.setPlainText(
                f"Archivo Original: {os.path.basename(self.filepath)} ({orig} bytes)\n"
                f"Archivo Comprimido: {os.path.basename(out)} ({comp} bytes)\n"
                f"Compresión real: {porcentaje_compresion:.2f}%\n"
                f"Dimensiones: {w}x{h}, píxeles: {total_pixels}\n"
                f"Corridas detectadas: {runs}\n"
                f"Promedio por corrida: {promedio_corrida:.2f}\n"
                f"Colores únicos: {len(unique_colors)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def decompress(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .rle", "", "RLE files (*.rle)")
        if fn:
            try:
                out = image_compressor.descomprimir_imagen(fn, OUT_DIR)
                QMessageBox.information(self, "Listo", f"Imagen reconstruida: {out}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))



class AudioView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        label = QLabel("Compresión de Audio (RLE)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #A5EFFF; font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        # Botones
        self.load_btn = QPushButton("Cargar Audio")
        self.comp_btn = QPushButton("Comprimir")
        self.decomp_btn = QPushButton("Descomprimir")
        for b in (self.load_btn, self.comp_btn, self.decomp_btn):
            b.setMinimumHeight(50)
            b.setStyleSheet("""
                QPushButton {
                    background-color: #00B8D9;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                }
                QPushButton:hover { background-color: #00A3C4; }
                QPushButton:pressed { background-color: #008EA8; }
            """)
            layout.addWidget(b)

        # Área de resultados
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("""
            QTextEdit {
                background: #2B2B2B;
                color: #CFCFCF;
                border: 1px solid #3E3E3E;
                border-radius: 10px;
                padding: 12px;
                font-family: Consolas;
                font-size: 15px;
            }
        """)
        layout.addWidget(self.result)

        self.filepath = None
        self.load_btn.clicked.connect(self.load_file)
        self.comp_btn.clicked.connect(self.compress)
        self.decomp_btn.clicked.connect(self.decompress)

    def load_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", "Audio files (*.wav *.mp3 *.flac)")
        if fn:
            self.filepath = fn
            size = format_size(os.path.getsize(fn))
            self.result.setPlainText(f"🎵 {os.path.basename(fn)} ({size})")

    def compress(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero un archivo de audio")
            return
        try:
            out, stats = audio_compressor.comprimir_wav(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)

            import pickle
            with open(out, 'rb') as f:
                params, compressed = pickle.load(f)
                nch, sampwidth, fr, nframes, *_ = params

            total_muestras = nframes * nch
            corridas = len(compressed)
            promedio_corrida = total_muestras / corridas if corridas != 0 else 0
            porcentaje_compresion = (1 - (comp / orig)) * 100 if orig != 0 else 0

            self.result.setPlainText(
                f"Archivo Original: {os.path.basename(self.filepath)} ({orig} bytes)\n"
                f"Archivo Comprimido: {os.path.basename(out)} ({comp} bytes)\n"
                f"Compresión real: {porcentaje_compresion:.2f}%\n"
                f"Canales: {nch}\n"
                f"Profundidad de bits: {sampwidth*8}\n"
                f"Muestras totales: {total_muestras}\n"
                f"Corridas detectadas: {corridas}\n"
                f"Promedio por corrida: {promedio_corrida:.2f}\n"
                f"Frecuencia: {fr} Hz\n"
                f"Notas: {stats}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def decompress(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .arle", "", "Audio-RLE files (*.arle)")
        if fn:
            try:
                out = audio_compressor.descomprimir_wav(fn, OUT_DIR)
                QMessageBox.information(self, "Listo", f"Audio reconstruido: {out}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))



# ====== INTERFAZ PRINCIPAL ======
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compresor de Datos Profesional")
        self.resize(1200, 700)  
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # ===== PANEL LATERAL =====
        side_panel = QFrame()
        side_panel.setFixedWidth(250)
        side_panel.setStyleSheet("QFrame {background-color: #101820; border-radius: 10px;}")
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(25, 30, 25, 25)
        side_layout.setSpacing(25)

        title = QLabel("💠 Panel de Control")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #A5EFFF; font-size: 18px; font-weight: bold;")
        side_layout.addWidget(title)

        self.btn_texto = QPushButton("Texto")
        self.btn_imagen = QPushButton("Imagen")
        self.btn_audio = QPushButton("Audio")

        for btn in (self.btn_texto, self.btn_imagen, self.btn_audio):
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0E2E38;
                    color: #D6F8FF;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #00B8D9; color: white; }
                QPushButton:checked {
                    background-color: #00B8D9;
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            side_layout.addWidget(btn)

        side_layout.addStretch()

        # ===== PANEL PRINCIPAL =====
        self.main_content = QFrame()
        self.main_content.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2E2E2E;
                border-radius: 12px;
            }
        """)
        self.content_layout = QVBoxLayout(self.main_content)
        self.content_layout.setContentsMargins(30, 30, 30, 30)

        self.views = {
            "texto": TextoView(),
            "imagen": ImagenView(),
            "audio": AudioView()
        }
        self.current_view = None
        self.set_view("texto")

        self.btn_texto.clicked.connect(lambda: self.set_view("texto"))
        self.btn_imagen.clicked.connect(lambda: self.set_view("imagen"))
        self.btn_audio.clicked.connect(lambda: self.set_view("audio"))

        main_layout.addWidget(side_panel)
        main_layout.addWidget(self.main_content)
        self.setCentralWidget(main_widget)

    def set_view(self, key):
        for btn in (self.btn_texto, self.btn_imagen, self.btn_audio):
            btn.setChecked(False)

        if key == "texto":
            self.btn_texto.setChecked(True)
        elif key == "imagen":
            self.btn_imagen.setChecked(True)
        elif key == "audio":
            self.btn_audio.setChecked(True)

        if self.current_view:
            self.content_layout.removeWidget(self.current_view)
            self.current_view.hide()

        self.current_view = self.views[key]
        self.content_layout.addWidget(self.current_view)
        self.current_view.show()

# ====== MAIN ======
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
