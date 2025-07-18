import sys
import os
import json
import webbrowser
import xml.etree.ElementTree as ET

from PIL import Image, ExifTags
import piexif
import pillow_heif

from PySide6.QtCore import Qt, QUrl, QTimer, QPointF
from PySide6.QtGui import (
    QPixmap, QIcon, QAction, QPainter, QColor, 
    QFont, QPen, QBrush, QFontMetrics, QDesktopServices
)
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QPushButton, QLabel, QWidget,
    QFileDialog, QTableWidget, QTableWidgetItem, QHBoxLayout,
    QMessageBox, QHeaderView, QLineEdit, QSystemTrayIcon, 
    QMenu, QSizeGrip, QStackedLayout, QDialog, QDialogButtonBox,
    QPlainTextEdit
)

pillow_heif.register_heif_opener()

from background import NetworkBackground

class MetadataViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TODO HACK OFFICIAL")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.old_pos = None
        icon_path = os.path.join(os.path.abspath("."), "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            self.tray_icon = QSystemTrayIcon(self)
        
        self.setGeometry(200, 100, 1000, 720)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #39FF14;
            }
            QMessageBox {
                background-color: #111;
            }
            QPushButton {
                background-color: #111;
                color: #39FF14;
                padding: 8px;
                border: 1px solid #39FF14;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #222;
            }
            QPushButton:pressed {
                background-color: #333;
            }
            QPushButton:disabled {
                background-color: #111;
                color: #555;
                border-color: #555;
            }
        """) 

        self.tray_icon.setToolTip("TODO HACK OFFICIAL")

        tray_menu = QMenu()

        restore_action = QAction("Mostrar ventana", self)
        restore_action.triggered.connect(self.show_normal_from_tray)
        tray_menu.addAction(restore_action)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)

        self.image_path = None
        self.image_list = []
        self.current_index = -1
        self.exif_data = {}
        self.exif_raw = {}
        self.is_maximized = False

        self.init_ui()
    
    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                self.minimize_to_tray()
                event.ignore()
            else:
                super().changeEvent(event)
        else:
            super().changeEvent(event)

    def minimize_to_tray(self):
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage("TODO HACK OFFICIAL", "La aplicación sigue activa en segundo plano.", QSystemTrayIcon.MessageIcon.Information, 3000)

    def show_normal_from_tray(self):            
        self.show()
        self.tray_icon.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if not self.is_maximized and self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def toggle_maximize_restore(self):
        if self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    def init_ui(self):
        
        central_layout = QVBoxLayout(self)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #111; border-width: 0 0 1px 0; border-style: solid; border-color: #39FF14;")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)

        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join(os.path.abspath("."), "logo.png")).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setStyleSheet("border: none;")

        title_label = QLabel("THO EXIF FORENSE | BY HANNIBAL THO| DISCORD .gg/8Ntx8cDSGT")
        title_label.setStyleSheet("color: #39FF14; font-size: 16px; font-weight: bold; border: none;")

        btn_style = """
            QPushButton {
                background-color: transparent;
                color: #39FF14;
                font-size: 20px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: white;
            }
        """

        minimize_button = QPushButton("-")
        minimize_button.setStyleSheet(btn_style)
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)

        maximize_button = QPushButton("▫")
        maximize_button.setStyleSheet(btn_style)
        maximize_button.setFixedSize(30, 30)
        maximize_button.clicked.connect(self.toggle_maximize_restore)

        close_button = QPushButton("x")
        close_button.setStyleSheet(btn_style)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)

        title_bar_layout.addWidget(logo_label)
        title_bar_layout.addSpacing(10)
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(minimize_button)
        title_bar_layout.addWidget(maximize_button)
        title_bar_layout.addWidget(close_button)

        central_layout.addWidget(title_bar)

        banner_label = QLabel("TODO HACK OFFICIAL")
        banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_label.setStyleSheet("""
            background-color: #0A0A0A;
            color: #39FF14;
            font-size: 18px;
            font-weight: bold;
            padding: 5px;
            border-bottom: 1px solid #39FF14;
        """)
        central_layout.addWidget(banner_label)

        ui_content_widget = QWidget()
        ui_content_widget.setStyleSheet("background-color: transparent; color: #39FF14;")
        layout = QVBoxLayout(ui_content_widget)

        self.header_label = QLabel("Ninguna imagen seleccionada")
        self.header_label.setStyleSheet("background-color: rgba(17, 17, 17, 0.8); color: #39FF14; font-size: 16px; padding: 8px; border-radius: 5px;")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.header_label)

        self.image_label = QLabel("Arrastra una imagen aquí")
        self.image_label.setFixedHeight(400)
        self.image_label.setStyleSheet("border: 2px dashed #39FF14; margin-bottom: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.3);")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        btn_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                background-color: #111;
                color: #39FF14;
                padding: 8px;
                border: 1px solid #39FF14;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #222;
            }
            QPushButton:pressed {
                background-color: #333;
            }
        """

        self.load_btn = QPushButton("Cargar Imagen Manualmente")
        self.load_btn.setStyleSheet(button_style)
        self.load_btn.clicked.connect(self.load_image)
        btn_layout.addWidget(self.load_btn)

        self.reload_btn = QPushButton("Limpiar Viewer")
        self.reload_btn.setStyleSheet(button_style)
        self.reload_btn.clicked.connect(self.reset_view)
        btn_layout.addWidget(self.reload_btn)

        self.clean_btn = QPushButton("Limpiar EXIF")
        self.clean_btn.setStyleSheet(button_style)
        self.clean_btn.clicked.connect(self.clean_exif)
        btn_layout.addWidget(self.clean_btn)

        self.gps_btn = QPushButton("No hay datos GPS")
        self.gps_btn.setEnabled(False)
        self.gps_btn.setStyleSheet("""
            QPushButton {
                background-color: #111;
                color: #555;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        self.gps_btn.clicked.connect(self.show_gps_location)
        btn_layout.addWidget(self.gps_btn)

        layout.addLayout(btn_layout)

        self.export_btn = QPushButton("Exportar metadatos")
        self.export_btn.setStyleSheet(button_style)
        self.export_btn.clicked.connect(self.export_metadata)
        layout.addWidget(self.export_btn)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrar metadatos...")
        self.filter_input.setStyleSheet("background-color: #111; color: #39FF14; border: 1px solid #39FF14; padding: 5px; border-radius: 5px;")
        self.filter_input.textChanged.connect(self.filter_metadata)
        layout.addWidget(self.filter_input)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Anterior")
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.clicked.connect(self.load_prev_image)

        self.next_btn = QPushButton("Siguiente →")
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.clicked.connect(self.load_next_image)

        self.image_counter = QLabel("")
        self.image_counter.setStyleSheet("color: #39FF14; font-size: 12px; padding: 4px;")

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.image_counter)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Campo", "Valor"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #000000;
                color: #39FF14;
                border: 1px solid #39FF14;
                gridline-color: #39FF14;
            }
            QHeaderView::section {
                background-color: #111;
                color: #39FF14;
                padding: 4px;
                border: 1px solid #39FF14;
            }
            QTableCornerButton::section {
                background-color: #111;
            }
        """)
        self.table.itemClicked.connect(self.show_xml_popup)
        layout.addWidget(self.table)

        footer = QWidget()
        footer.setFixedHeight(20)
        footer.setStyleSheet("background-color: #111; border-top: 1px solid #39FF14;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(0)

        sizegrip = QSizeGrip(self)
        sizegrip.setStyleSheet("background-color: transparent;")

        footer_layout.addStretch()
        footer_layout.addWidget(sizegrip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        central_layout.addWidget(footer)

        background_widget = NetworkBackground()

        stacked_layout = QStackedLayout()
        stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        stacked_layout.addWidget(background_widget)
        stacked_layout.addWidget(ui_content_widget)
        
        container = QWidget()
        container.setLayout(stacked_layout)
        central_layout.addWidget(container)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [
            u.toLocalFile() for u in urls
            if u.toLocalFile().lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp', '.gif', '.heic'))
        ]
        if paths:
            self.image_list = paths
            self.current_index = 0
            self.load_image_from_path(self.image_list[self.current_index])
        else:
            QMessageBox.warning(self, "Formato no válido", "Solo se permiten imágenes con formato compatible.")

    def reset_view(self):
        self.image_label.clear()
        self.image_label.setText("Arrastra una imagen aquí")
        self.header_label.setText("Ninguna imagen seleccionada")
        self.filter_input.clear()
        self.table.setRowCount(0)
        self.image_path = None
        self.exif_data = {}
        self.exif_raw = {}
        self.image_list = []
        self.current_index = -1
        self.image_counter.setText("")

    def load_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters([
            "Imágenes (*.jpg *.jpeg *.png *.tiff *.bmp *.webp *.gif *.heic)",
            "Todos los archivos (*)"
        ])
        if file_dialog.exec():
            file_name = file_dialog.selectedFiles()[0]
            self.load_image_from_path(file_name)

    def load_image_from_path(self, file_name):
        try:
            img = Image.open(file_name)
            img.verify()
            self.image_path = file_name
            self.header_label.setText(os.path.basename(file_name))
            self.load_metadata()
            self.display_image()
            if self.image_list:
                self.image_counter.setText(f"{self.current_index + 1} / {len(self.image_list)}")
            else:
                self.image_counter.setText("")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la imagen:\n{e}")

    def load_metadata(self):
        from PIL.TiffImagePlugin import IFDRational
        from PIL import ExifTags

        self.exif_data = {}
        self.exif_raw = {}
        self.table.setRowCount(0)

        if not self.image_path:
            return

        try:
            img = Image.open(self.image_path)
            exif_dict = {}
            self.exif_raw = {}

            exif_bytes = img.info.get("exif", None)
            if exif_bytes:
                try:
                    piexif_data = piexif.load(exif_bytes)
                    self.exif_raw = piexif_data
                    for ifd_name in piexif_data:
                        if ifd_name == "thumbnail":
                            continue
                        for tag_id, value in piexif_data[ifd_name].items():
                            try:
                                tag_name = f"{ifd_name}:{tag_id}"
                                if isinstance(value, tuple) and len(value) == 2:
                                    try:
                                        value = float(value[0]) / float(value[1]) if value[1] != 0 else 0
                                    except:
                                        value = str(value)
                                elif isinstance(value, bytes):
                                    try:
                                        value = value.decode('utf-8', errors='ignore')
                                    except:
                                        value = f"[Bytes: {len(value)}]"
                                exif_dict[tag_name] = value
                            except Exception as e:
                                print(f"Error processing tag {tag_id}: {e}")
                except Exception as e:
                    print("piexif error:", e)

            try:
                exif = img.getexif()
                for tag_id, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
                    if isinstance(value, IFDRational):
                        value = float(value)
                    elif isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = f"[Bytes: {len(value)}]"
                    exif_dict[tag_name] = value
            except Exception as e:
                print("getexif error:", e)

            if not exif_dict and img.info:
                for k, v in img.info.items():
                    exif_dict[k] = str(v)

            if not exif_dict:
                QMessageBox.information(self, "Sin metadatos", "No se han encontrado metadatos reconocibles.")
                return

            self.exif_data = exif_dict
            self.display_metadata()
            self.check_gps_button()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo extraer metadatos:\n{e}")

    def display_metadata(self):
        self.table.setRowCount(0)

        for row, (key, value) in enumerate(self.exif_data.items()):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(key)))

            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except:
                    value = f"[Bytes: {len(value)}]"

            is_xml = False
            try:
                if isinstance(value, str) and (value.strip().startswith('<?xpacket') or value.strip().startswith('<')):
                    ET.fromstring(value)
                    is_xml = True
            except:
                pass

            if is_xml:
                preview = "(XML detectado - doble clic para ver)"
                item = QTableWidgetItem(preview)
                item.setData(Qt.UserRole, value)  
                self.table.setItem(row, 1, item)
            else:
                self.table.setItem(row, 1, QTableWidgetItem(str(value)))

        self.table.itemDoubleClicked.connect(self.show_xml_popup)

    def show_xml_popup(self, item):
        if item.column() != 1:
            return

        value = item.data(Qt.UserRole)
        if not value:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Vista del contenido XML")
        dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout()

        viewer = QPlainTextEdit()
        viewer.setPlainText(value)
        viewer.setReadOnly(True)
        viewer.setStyleSheet("background-color: #1e1e1e; color: #83f1e8; font-family: Consolas; font-size: 12px;")
        layout.addWidget(viewer)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def display_image(self):
        if not self.image_path:
            return
        try:
            img = Image.open(self.image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            temp_path = os.path.join(os.path.dirname(__file__), '_temp_preview.jpg')
            img.save(temp_path, format='JPEG')
            pixmap = QPixmap(temp_path)
            scaled = pixmap.scaledToHeight(380, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            os.remove(temp_path)
        except Exception as e:
            self.image_label.setText("No se pudo mostrar la imagen")
            print(f"Error mostrando imagen: {e}")

    def filter_metadata(self):
        search = self.filter_input.text().lower()
        for row in range(self.table.rowCount()):
            item_key = self.table.item(row, 0).text().lower()
            item_value = self.table.item(row, 1).text().lower()
            is_visible = search in item_key or search in item_value
            self.table.setRowHidden(row, not is_visible)

    def clean_exif(self):
        if not self.image_path:
            return
        try:
            img = Image.open(self.image_path)
            new_path, _ = QFileDialog.getSaveFileName(self, "Guardar como", "", "Imagen JPEG (*.jpg);;Todos los archivos (*)")
            if new_path:
                img.save(new_path, exif=piexif.dump({"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}))
                QMessageBox.information(self, "Limpieza", "Metadatos EXIF eliminados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al limpiar los metadatos:\n{e}")

    def export_metadata(self):
        if not self.exif_data:
            QMessageBox.information(self, "Exportación", "No hay metadatos para exportar.")
            return

        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar metadatos como", "metadata.json", "JSON (*.json);;Texto (*.txt)", options=options)
        if filename:
            try:
                if filename.endswith('.txt'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        for key, value in self.exif_data.items():
                            f.write(f"{key}: {value}\n")
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.exif_data, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "Éxito", f"Metadatos exportados a {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")

    def check_gps_button(self):
        if piexif.GPSIFD in self.exif_raw:
            self.gps_btn.setText("Ver Ubicación GPS")
            self.gps_btn.setEnabled(True)
            self.gps_btn.setStyleSheet("""
                QPushButton {
                    background-color: #111;
                    color: #39FF14;
                    padding: 8px;
                    border: 1px solid #39FF14;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #222;
                }
                QPushButton:pressed {
                    background-color: #333;
                }
            """)
        else:
            self.gps_btn.setText("No hay datos GPS")
            self.gps_btn.setEnabled(False)
            self.gps_btn.setStyleSheet("""
                QPushButton {
                    background-color: #111;
                    color: #555;
                    padding: 8px;
                    border: 1px solid #555;
                    border-radius: 5px;
                }
            """)

    def show_gps_location(self):
        gps_info = self.exif_raw.get("GPS", {})
        if not gps_info:
            return

        def dms_to_deg(value):
            return value[0][0] / value[0][1] + value[1][0] / value[1][1] / 60 + value[2][0] / value[2][1] / 3600

        try:
            lat = dms_to_deg(gps_info[2])
            if gps_info[1] == b'S':
                lat = -lat
            lon = dms_to_deg(gps_info[4])
            if gps_info[3] == b'W':
                lon = -lon

            url = f"https://www.google.com/maps?q={lat},{lon}&z=15"
            lat_ref = "N" if lat >= 0 else "S"
            lon_ref = "E" if lon >= 0 else "W"
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Ubicación GPS")
            dialog.setMinimumSize(400, 300)
            layout = QVBoxLayout()

            info_label = QLabel(f"Coordenadas encontradas:\nLatitud: {abs(lat):.6f}° {lat_ref}\nLongitud: {abs(lon):.6f}° {lon_ref}")
            info_label.setStyleSheet("color: #39FF14; font-size: 14px; padding: 10px;")
            layout.addWidget(info_label)

            buttons = QDialogButtonBox()
            copy_btn = QPushButton("Copiar Coordenadas")
            maps_btn = QPushButton("Abrir en Google Maps")
            close_btn = QPushButton("Cerrar")
            
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(f"{lat}, {lon}"))
            maps_btn.clicked.connect(lambda: webbrowser.open(url))
            close_btn.clicked.connect(dialog.close)
            
            buttons.addButton(copy_btn, QDialogButtonBox.ActionRole)
            buttons.addButton(maps_btn, QDialogButtonBox.ActionRole)
            buttons.addButton(close_btn, QDialogButtonBox.RejectRole)

            layout.addWidget(buttons)
            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QMessageBox.warning(self, "GPS", f"Error al obtener coordenadas:\n{e}")

    def load_prev_image(self):
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.load_image_from_path(self.image_list[self.current_index])

    def load_next_image(self):
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.load_image_from_path(self.image_list[self.current_index])

    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = MetadataViewer()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)
