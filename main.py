import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTextEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QProgressBar
from PyQt5.QtCore import Qt
from compresion import text_compressor, image_compressor, audio_compressor

OUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

#TEXTO
class TextoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.info = QLabel("Selecciona un archivo .txt")
        layout.addWidget(self.info)
        btns = QHBoxLayout()
        self.cargar_btn = QPushButton("Cargar .txt")
        self.comprimir_btn = QPushButton("Comprimir (Huffman)")
        self.descomprimir_btn = QPushButton("Descomprimir .bin")
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
        out = text_compressor.comprimir_archivo(self.filepath, OUT_DIR)
        orig = os.path.getsize(self.filepath)
        comp = os.path.getsize(out)
        self.resultado.setPlainText(f"Comprimido: {out}\nTamaño original: {orig} bytes\nTamaño comprimido: {comp} bytes")

    def decompress(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .bin (Huffman)", "", "Binary files (*.bin);;All files (*)")
        if not fn:
            return
        out = text_compressor.descomprimir_archivo(fn, OUT_DIR)
        QMessageBox.information(self, "Hecho", f"Archivo descomprimido: {out}")

#IMAGEN
class ImagenTab(QWidget):
    def __init__(self):
        super().__init__(); self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.info = QLabel("Selecciona una imagen (.png/.bmp)")
        layout.addWidget(self.info)
        btns = QHBoxLayout()
        self.load_btn = QPushButton("Cargar imagen")
        self.compress_btn = QPushButton("Comprimir (RLE)")
        self.decompress_btn = QPushButton("Descomprimir .rle")
        btns.addWidget(self.load_btn); btns.addWidget(self.compress_btn); btns.addWidget(self.decompress_btn)
        layout.addLayout(btns)
        self.result = QTextEdit(); self.result.setReadOnly(True); layout.addWidget(self.result)
        self.setLayout(layout)

        self.filepath = None
        self.load_btn.clicked.connect(self.cargar_archivo)
        self.compress_btn.clicked.connect(self.comprimir)
        self.decompress_btn.clicked.connect(self.descomprimir)

    def cargar_archivo(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.bmp)")
        if fn:
            self.filepath = fn
            self.info.setText(f"Imagen: {fn}")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero una imagen")
            return
        out = image_compressor.comprimir_imagen(self.filepath, OUT_DIR)
        orig = os.path.getsize(self.filepath)
        comp = os.path.getsize(out)
        self.result.setPlainText(f"Comprimido: {out}\nTamaño original: {orig} bytes\nTamaño comprimido: {comp} bytes")

    def descomprimir(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .rle", "", "RLE files (*.rle);;All files (*)")
        if not fn:
            return
        out = image_compressor.descomprimir_imagen(fn, OUT_DIR)
        QMessageBox.information(self, "Hecho", f"Imagen reconstruida: {out}")

#AUDIO
class AudioTab(QWidget):
    def __init__(self):
        super().__init__(); self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        self.info = QLabel("Selecciona un audio .wav (16-bit PCM preferible)")
        layout.addWidget(self.info)
        btns = QHBoxLayout()
        self.load_btn = QPushButton("Cargar .wav")
        self.compress_btn = QPushButton("Comprimir (RLE adaptado)")
        self.decompress_btn = QPushButton("Descomprimir .arle")
        btns.addWidget(self.load_btn); btns.addWidget(self.compress_btn); btns.addWidget(self.decompress_btn)
        layout.addLayout(btns)
        self.result = QTextEdit(); self.result.setReadOnly(True); layout.addWidget(self.result)
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
        out, stats = audio_compressor.comprimir_wav(self.filepath, OUT_DIR)
        orig = os.path.getsize(self.filepath)
        comp = os.path.getsize(out)
        self.result.setPlainText(f"Comprimido: {out}\nTamaño original: {orig} bytes\nTamaño comprimido: {comp} bytes\nNotas: {stats}")

    def descomprimir(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .arle", "", "Audio-RLE files (*.arle);;All files (*)")
        if not fn:
            return
        out = audio_compressor.descomprimir_wav(fn, OUT_DIR)
        QMessageBox.information(self, "Hecho", f"Audio reconstruido: {out}")

#VENTANA PRINCIPAL
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compresor de Datos - PyQt5")
        tabs = QTabWidget()
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
