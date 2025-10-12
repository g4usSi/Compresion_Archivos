import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTextEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from compresion import text_compressor, image_compressor, audio_compressor

OUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

def format_size(bytes_size):
    """Convierte bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_compression_ratio(original, compressed):
    """Calcula ratio de compresión"""
    if original == 0:
        return 0
    return ((original - compressed) / original) * 100

#TEXTO
class TextoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Info del archivo
        self.info = QLabel("📄 Selecciona un archivo .txt para comenzar")
        self.info.setStyleSheet("font-size: 13px; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.info)
        
        # Botones
        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.cargar_btn = QPushButton("📂 Cargar Archivo")
        self.comprimir_btn = QPushButton("🗜️ Comprimir")
        self.descomprimir_btn = QPushButton("📦 Descomprimir")
        
        for btn in [self.cargar_btn, self.comprimir_btn, self.descomprimir_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #45a049; }
                QPushButton:pressed { background: #3d8b40; }
            """)
        
        btns.addWidget(self.cargar_btn)
        btns.addWidget(self.comprimir_btn)
        btns.addWidget(self.descomprimir_btn)
        layout.addLayout(btns)
        
        # Resultado
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("background: #fafafa; border: 1px solid #ddd; border-radius: 5px; padding: 10px; font-family: Consolas, monospace;")
        layout.addWidget(self.resultado)
        
        self.setLayout(layout)
        self.filepath = None
        
        self.cargar_btn.clicked.connect(self.cargar_archivo)
        self.comprimir_btn.clicked.connect(self.comprimir)
        self.descomprimir_btn.clicked.connect(self.decompress)

    def cargar_archivo(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar txt", "", "Text files (*.txt)")
        if fn:
            self.filepath = fn
            name = os.path.basename(fn)
            size = format_size(os.path.getsize(fn))
            self.info.setText(f"📄 {name} ({size})")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero un archivo .txt")
            return
        
        try:
            out = text_compressor.comprimir_archivo(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)
            ratio = get_compression_ratio(orig, comp)
            
            resultado_texto = f"""
╔══════════════════════════════════════════════════════╗
║              COMPRESIÓN HUFFMAN EXITOSA              ║
╚══════════════════════════════════════════════════════╝

📁 Archivo Original:    {os.path.basename(self.filepath)}
📊 Tamaño Original:     {format_size(orig)} ({orig:,} bytes)

📦 Archivo Comprimido:  {os.path.basename(out)}
📊 Tamaño Comprimido:   {format_size(comp)} ({comp:,} bytes)

🎯 Ratio de Compresión: {ratio:.2f}%
💾 Espacio Ahorrado:    {format_size(orig - comp)}

✅ Ubicación: {out}
            """
            self.resultado.setPlainText(resultado_texto.strip())
        except Exception as e:
            QMessageBox.critical(self, "Error de Compresión", 
                f"Error al comprimir el archivo:\n{str(e)}\n\n"
                f"Sugerencia: Verifica que el archivo sea un .txt válido y "
                f"esté codificado en UTF-8 o Latin-1.")

    def decompress(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .bin", "", "Binary files (*.bin);;All files (*)")
        if not fn:
            return
        try:
            out = text_compressor.descomprimir_archivo(fn, OUT_DIR)
            QMessageBox.information(self, "✅ Completado", f"Archivo descomprimido:\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al descomprimir:\n{str(e)}")

#IMAGEN
class ImagenTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        self.info = QLabel("🖼️ Selecciona una imagen (.png/.bmp)")
        self.info.setStyleSheet("font-size: 13px; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.info)
        
        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.load_btn = QPushButton("📂 Cargar Imagen")
        self.compress_btn = QPushButton("🗜️ Comprimir")
        self.decompress_btn = QPushButton("📦 Descomprimir")
        
        for btn in [self.load_btn, self.compress_btn, self.decompress_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #0b7dda; }
                QPushButton:pressed { background: #0a6bc4; }
            """)
        
        btns.addWidget(self.load_btn)
        btns.addWidget(self.compress_btn)
        btns.addWidget(self.decompress_btn)
        layout.addLayout(btns)
        
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("background: #fafafa; border: 1px solid #ddd; border-radius: 5px; padding: 10px; font-family: Consolas, monospace;")
        layout.addWidget(self.result)
        
        self.setLayout(layout)
        self.filepath = None
        
        self.load_btn.clicked.connect(self.cargar_archivo)
        self.compress_btn.clicked.connect(self.comprimir)
        self.decompress_btn.clicked.connect(self.descomprimir)

    def cargar_archivo(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.bmp)")
        if fn:
            self.filepath = fn
            name = os.path.basename(fn)
            size = format_size(os.path.getsize(fn))
            self.info.setText(f"🖼️ {name} ({size})")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero una imagen")
            return
        
        try:
            out = image_compressor.comprimir_imagen(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)
            ratio = get_compression_ratio(orig, comp)
            
            resultado_texto = f"""
╔══════════════════════════════════════════════════════╗
║               COMPRESIÓN RLE EXITOSA                 ║
╚══════════════════════════════════════════════════════╝

🖼️ Imagen Original:     {os.path.basename(self.filepath)}
📊 Tamaño Original:     {format_size(orig)} ({orig:,} bytes)

📦 Archivo Comprimido:  {os.path.basename(out)}
📊 Tamaño Comprimido:   {format_size(comp)} ({comp:,} bytes)

🎯 Ratio de Compresión: {ratio:.2f}%
💾 Espacio Ahorrado:    {format_size(orig - comp)}

✅ Ubicación: {out}
            """
            self.result.setPlainText(resultado_texto.strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al comprimir imagen:\n{str(e)}")

    def descomprimir(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .rle", "", "RLE files (*.rle);;All files (*)")
        if not fn:
            return
        try:
            out = image_compressor.descomprimir_imagen(fn, OUT_DIR)
            QMessageBox.information(self, "✅ Completado", f"Imagen reconstruida:\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al descomprimir:\n{str(e)}")

#AUDIO
class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        self.info = QLabel("🎵 Selecciona un audio .wav (16-bit PCM)")
        self.info.setStyleSheet("font-size: 13px; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.info)
        
        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.load_btn = QPushButton("📂 Cargar Audio")
        self.compress_btn = QPushButton("🗜️ Comprimir")
        self.decompress_btn = QPushButton("📦 Descomprimir")
        
        for btn in [self.load_btn, self.compress_btn, self.decompress_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background: #e68900; }
                QPushButton:pressed { background: #cc7a00; }
            """)
        
        btns.addWidget(self.load_btn)
        btns.addWidget(self.compress_btn)
        btns.addWidget(self.decompress_btn)
        layout.addLayout(btns)
        
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet("background: #fafafa; border: 1px solid #ddd; border-radius: 5px; padding: 10px; font-family: Consolas, monospace;")
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
            name = os.path.basename(fn)
            size = format_size(os.path.getsize(fn))
            self.info.setText(f"🎵 {name} ({size})")

    def comprimir(self):
        if not self.filepath:
            QMessageBox.warning(self, "Error", "Carga primero un archivo .wav")
            return
        
        try:
            out, stats = audio_compressor.comprimir_wav(self.filepath, OUT_DIR)
            orig = os.path.getsize(self.filepath)
            comp = os.path.getsize(out)
            ratio = get_compression_ratio(orig, comp)
            
            resultado_texto = f"""
╔══════════════════════════════════════════════════════╗
║            COMPRESIÓN AUDIO RLE EXITOSA              ║
╚══════════════════════════════════════════════════════╝

🎵 Audio Original:      {os.path.basename(self.filepath)}
📊 Tamaño Original:     {format_size(orig)} ({orig:,} bytes)

📦 Archivo Comprimido:  {os.path.basename(out)}
📊 Tamaño Comprimido:   {format_size(comp)} ({comp:,} bytes)

🎯 Ratio de Compresión: {ratio:.2f}%
💾 Espacio Ahorrado:    {format_size(orig - comp)}

📝 Estadísticas:        {stats}

✅ Ubicación: {out}
            """
            self.result.setPlainText(resultado_texto.strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al comprimir audio:\n{str(e)}")

    def descomprimir(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Seleccionar .arle", "", "Audio-RLE files (*.arle);;All files (*)")
        if not fn:
            return
        try:
            out = audio_compressor.descomprimir_wav(fn, OUT_DIR)
            QMessageBox.information(self, "✅ Completado", f"Audio reconstruido:\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al descomprimir:\n{str(e)}")

#VENTANA PRINCIPAL
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗜️ Compresor de Datos Profesional")
        
        # Estilo moderno para toda la ventana
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #f5f5f5;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 3px solid #2196F3;
            }
            QTabBar::tab:hover {
                background: #e8e8e8;
            }
        """)
        
        tabs = QTabWidget()
        tabs.addTab(TextoTab(), "📄 Texto (Huffman)")
        tabs.addTab(ImagenTab(), "🖼️ Imagen (RLE)")
        tabs.addTab(AudioTab(), "🎵 Audio (RLE)")
        
        self.setCentralWidget(tabs)
        self.resize(850, 650)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno multiplataforma
    w = VentanaPrincipal()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()