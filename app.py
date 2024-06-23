import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QComboBox, QTabWidget, QTextEdit, QLineEdit, QFormLayout,
    QMessageBox, QCheckBox, QFileDialog
)
from PyQt5.QtCore import QTimer, Qt, QUrl
import serial
import serial.serialutil
import serial.tools.list_ports
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import folium
from PyQt5.QtGui import QPixmap, QIcon
import webbrowser
import io
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atmaca Roket Takımı - Yer İstasyonu Veri İzleme Aracı")
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setFixedSize(1040, 680)  # setFixedSize yerine resize kullanıyoruz

        with open("config.json", "r") as file:
            self.config_json = json.loads(file.read())

            if self.config_json["theme"] == "White":
                with open("styles/style-white.qss", "r", encoding="utf-8") as style_file:
                    style_sheet = style_file.read()
                    self.setStyleSheet(style_sheet)
            elif self.config_json["theme"] == "Dark":
                with open("styles/style-dark.qss", "r", encoding="utf-8") as style_file:
                    style_sheet = style_file.read()
                    self.setStyleSheet(style_sheet)

        self.serial_port = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)

        self.test_mode = False
        self.show_test_mode = True
        self.test_data = {
            'name': 'Roket',
            'packageNumber': '123',
            'latitude': 41.015137,
            'longitude': 28.979530,
            'speed': 2,
            'pressure': '1013 hPa',
            'altitude': '25000 m',
            'temperature': '20°C',
            'pitch': '5°',
            'roll': '10°',
            'yaw': '15°',
            'pyroTrigger': 'No',
            'flightStatus': 'Ascending'
        }

        self.data_entries = {
            'name': QLineEdit(),
            'packageNumber': QLineEdit(),
            'latitude': QLineEdit(),
            'longitude': QLineEdit(),
            'speed': QLineEdit(),
            'pressure': QLineEdit(),
            'altitude': QLineEdit(),
            'temperature': QLineEdit(),
            'pitch': QLineEdit(),
            'roll': QLineEdit(),
            'yaw': QLineEdit(),
            'pyroTrigger': QLineEdit(),
            'flightStatus': QLineEdit(),
        }

        self.previous_map_data = {"latitude": None, "longitude": None}  # Önceki harita verilerini saklamak için değişken
        self.data_log = []
        self.altitude_data = []
        self.pressure_data = []
        self.speed_data = []
        self.time_data = []
        self.map_data = []

        self.window_widget_creator()

    def window_widget_creator(self):
        # Giriş Ekranı
        self.port_selection_layout = QVBoxLayout()

        # Resmi ekle
        image_label = QLabel(self)
        pixmap = QPixmap("resources/logo.png")
        pixmap = pixmap.scaledToWidth(450)  # Resmi genişliğe göre ölçeklendirin
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        self.port_label = QLabel("Port: ")
        self.port_combo = QComboBox()
        self.refresh_ports()

        self.baund_label = QLabel("Baund: ")
        self.baund_entry = QComboBox()
        self.baund_entry.addItems(["9600", "115200"])

        self.refresh_button = QPushButton("Yenile")
        self.refresh_button.clicked.connect(self.refresh_ports)

        self.connect_button = QPushButton("Bağla")
        self.connect_button.clicked.connect(self.connect_serial)

        if self.show_test_mode == True:
            self.test_mode_button = QPushButton("Test Modu")
            self.test_mode_button.clicked.connect(self.enable_test_mode)

        self.port_layout = QFormLayout()
        self.port_layout.addRow(self.port_label, self.port_combo)
        self.port_layout.addRow(self.baund_label, self.baund_entry)

        self.port_selection_layout.addSpacing(25)
        self.port_selection_layout.addWidget(image_label)
        self.port_selection_layout.addSpacing(50)
        self.port_selection_layout.addLayout(self.port_layout)
        self.port_selection_layout.addWidget(self.refresh_button)
        self.port_selection_layout.addWidget(self.connect_button)
        self.port_selection_layout.addStretch(1)
        if self.show_test_mode == True:
            self.port_selection_layout.addWidget(self.test_mode_button)

        self.port_selection_widget = QWidget()
        self.port_selection_widget.setLayout(self.port_selection_layout)

        self.setCentralWidget(self.port_selection_widget)

        # Ana Sekmeli Ekran
        self.tabs = QTabWidget()

        # Giriş Sekmesi
        self.entry_tab = QWidget()
        self.entry_layout = QVBoxLayout()
        self.entry_view = QWebEngineView()
        settings = QWebEngineSettings.globalSettings()
        settings.setDefaultTextEncoding("utf-8")
        self.entry_layout.addWidget(self.entry_view)
        self.entry_tab.setLayout(self.entry_layout)

        self.tabs.addTab(self.entry_tab, "Giriş")

        local_html_path = os.path.join(os.path.dirname(__file__), 'resources/entry.html')
        self.entry_view.setUrl(QUrl.fromLocalFile(local_html_path))

        # Veriler Sekmesi
        self.data_tab = QWidget()
        self.data_layout = QVBoxLayout()

        self.data_entries_layout = QFormLayout()

        self.data_entries_layout.addRow("Name:", self.data_entries['name'])
        self.data_entries_layout.addRow("Package Number:", self.data_entries['packageNumber'])
        self.data_entries_layout.addRow("Latitude:", self.data_entries['latitude'])
        self.data_entries_layout.addRow("Longitude:", self.data_entries['longitude'])
        self.data_entries_layout.addRow("Speed:", self.data_entries['speed'])
        self.data_entries_layout.addRow("Pressure:", self.data_entries['pressure'])
        self.data_entries_layout.addRow("Altitude:", self.data_entries['altitude'])
        self.data_entries_layout.addRow("Temperature:", self.data_entries['temperature'])
        self.data_entries_layout.addRow("Pitch:", self.data_entries['pitch'])
        self.data_entries_layout.addRow("Roll:", self.data_entries['roll'])
        self.data_entries_layout.addRow("Yaw:", self.data_entries['yaw'])
        self.data_entries_layout.addRow("Pyro Trigger:", self.data_entries['pyroTrigger'])
        self.data_entries_layout.addRow("Flight Status:", self.data_entries['flightStatus'])

        self.data_layout.addLayout(self.data_entries_layout)  # Layout eklendi
        self.data_layout.addStretch(1)  # Boşluk eklenerek alt kısmı genişletildi
        
        self.data_tab.setLayout(self.data_layout)
        self.tabs.addTab(self.data_tab, "Veriler")

        # Grafik Sekmesi
        self.graph_tab = QWidget()
        self.graph_layout = QVBoxLayout()

        self.graph_tabs = QTabWidget()

        # İrtifa Grafik Sekmesi
        self.altitude_tab = QWidget()
        self.altitude_layout = QVBoxLayout()
        self.altitude_fig, self.altitude_ax = plt.subplots()
        self.altitude_canvas = FigureCanvas(self.altitude_fig)
        self.altitude_toolbar = NavigationToolbar(self.altitude_canvas, self)
        self.altitude_layout.addWidget(self.altitude_toolbar)
        self.altitude_layout.addWidget(self.altitude_canvas)
        self.altitude_tab.setLayout(self.altitude_layout)
        self.graph_tabs.addTab(self.altitude_tab, "İrtifa")

        # Basınç Grafik Sekmesi
        self.pressure_tab = QWidget()
        self.pressure_layout = QVBoxLayout()
        self.pressure_fig, self.pressure_ax = plt.subplots()
        self.pressure_canvas = FigureCanvas(self.pressure_fig)
        self.pressure_toolbar = NavigationToolbar(self.pressure_canvas, self)
        self.pressure_layout.addWidget(self.pressure_toolbar)
        self.pressure_layout.addWidget(self.pressure_canvas)
        self.pressure_tab.setLayout(self.pressure_layout)
        self.graph_tabs.addTab(self.pressure_tab, "Basınç")

        # Hız Grafik Sekmesi
        self.speed_tab = QWidget()
        self.speed_layout = QVBoxLayout()
        self.speed_fig, self.speed_ax = plt.subplots()
        self.speed_canvas = FigureCanvas(self.speed_fig)
        self.speed_toolbar = NavigationToolbar(self.speed_canvas, self)
        self.speed_layout.addWidget(self.speed_toolbar)
        self.speed_layout.addWidget(self.speed_canvas)
        self.speed_tab.setLayout(self.speed_layout)
        self.graph_tabs.addTab(self.speed_tab, "Hız")

        self.graph_layout.addWidget(self.graph_tabs)
        self.graph_tab.setLayout(self.graph_layout)
        self.tabs.addTab(self.graph_tab, "Grafikler")

        # Harita Sekmesi
        self.map_tab = QWidget()
        self.map_layout = QVBoxLayout()
        self.map_view = QWebEngineView()
        self.map_layout.addWidget(self.map_view)

        self.map_checkbox_layout = QVBoxLayout()
        self.map_checkbox = QCheckBox("Haritayı Otomatik Güncelle")
        self.map_checkbox.setChecked(True)
        self.map_checkbox.stateChanged.connect(self.check_map_data_changed)
        self.map_checkbox_layout.addWidget(self.map_checkbox)
        
        self.open_google_maps_button = QPushButton("Google Maps'te Aç")
        self.open_google_maps_button.clicked.connect(self.open_google_maps)

        self.map_layout.addLayout(self.map_checkbox_layout)
        self.map_layout.addWidget(self.open_google_maps_button)

        self.map_tab.setLayout(self.map_layout)
        self.tabs.addTab(self.map_tab, "Harita")

        #Seri Port Sekmesi
        self.serial_data_tab = QWidget()
        self.serial_data_layout = QVBoxLayout()

        self.serial_data_text = QTextEdit()
        self.serial_data_text.setReadOnly(True)

        self.serial_data_layout.addWidget(self.serial_data_text)
        self.serial_data_tab.setLayout(self.serial_data_layout)

        self.tabs.addTab(self.serial_data_tab, "Seri Port")

        # Ayarlar Sekmesi
        self.system_info_text_edit = QTextEdit()
        self.system_info_text_edit.setReadOnly(True)
        self.system_info_text_edit.setFixedSize(1040, 150)
        self.system_info_text_edit.setPlainText("Sistem bilgisi yok.")

        self.refresh_system_info_button = QPushButton("Yenile")
        self.refresh_system_info_button.clicked.connect(self.refresh_system_info)

        self.disconnect_button = QPushButton("Bağlantıyı Kes")
        self.disconnect_button.clicked.connect(self.disconnect_serial)

        self.save_data_button = QPushButton("Verileri Kaydet")
        self.save_data_button.clicked.connect(self.save_as_data)

        self.change_app_theme_layout = QFormLayout()
        self.change_app_theme_selector = QComboBox()
        self.change_app_theme_selector.addItem("Açık")
        self.change_app_theme_selector.addItem("Koyu")
        if self.config_json["theme"] == "White":
            self.change_app_theme_selector.setCurrentText("Açık")
        if self.config_json["theme"] == "Dark":
            self.change_app_theme_selector.setCurrentText("Koyu")
        self.change_app_theme_selector.currentIndexChanged.connect(self.change_app_theme)
        self.change_app_theme_layout.addRow("Tema:", self.change_app_theme_selector)

        self.settings_tab = QWidget()
        self.settings_layout = QVBoxLayout()
        self.settings_layout.addWidget(self.system_info_text_edit)
        self.settings_layout.addWidget(self.refresh_system_info_button)
        self.settings_layout.addWidget(self.disconnect_button)
        self.settings_layout.addSpacing(20)
        self.settings_layout.addWidget(self.save_data_button)
        self.settings_layout.addSpacing(40)
        self.settings_layout.addLayout(self.change_app_theme_layout)

        self.settings_tab.setLayout(self.settings_layout)
        self.tabs.addTab(self.settings_tab, "Ayarlar")

        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_layout.addWidget(self.tabs)
        self.central_widget.setLayout(self.central_layout)

    def change_app_theme(self):
        if self.change_app_theme_selector.currentIndex() == 0:
            with open("styles/style-white.qss", "r", encoding="utf-8") as style_file:
                style_sheet = style_file.read()
                self.setStyleSheet(style_sheet)
            self.config_json["theme"] = "White"
            with open("config.json", "w", encoding="utf-8") as file:
                json.dump(self.config_json, file, indent=4, ensure_ascii=False)
        elif self.change_app_theme_selector.currentIndex() == 1:
            with open("styles/style-dark.qss", "r", encoding="utf-8") as style_file:
                style_sheet = style_file.read()
                self.setStyleSheet(style_sheet)
            self.config_json["theme"] = "Dark"
            with open("config.json", "w", encoding="utf-8") as file:
                json.dump(self.config_json, file, indent=4, ensure_ascii=False)

    def enable_test_mode(self):
        self.test_mode = True
        self.show_test_mode = False
        self.setCentralWidget(self.central_widget)
        self.refresh_system_info()

        self.update_map(self.test_data['latitude'], self.test_data['longitude'])
        self.update_graphs(self.test_data)
        self.update_data_display(self.test_data)
        self.save_data(self.test_data)

    def refresh_ports(self):
        self.port_combo.clear()
        self.port_combo.addItem("--Port--")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def connect_serial(self):
        try:
            port = self.port_combo.currentText()
            baund = int(self.baund_entry.currentText())
            if port == "--Port--":
                self.show_message("Hata", "Lütfen geçerli bir port seçin.")
            else:
                self.serial_port = serial.Serial(port, baund, timeout=1)
                self.setCentralWidget(self.central_widget)
                self.refresh_system_info()
                self.timer.start(1000)
        except serial.SerialException as e:
            self.show_message("Seri Port Hatası", str(e))
        except ValueError as e:
            self.show_message("Hata", "Geçersiz baund hızı. Lütfen bir tam sayı girin.")
        except Exception as e:
            self.show_message("Hata", str(e))

    def read_serial_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode("utf-8").strip()
                self.serial_data_text.append(line)
                if line:
                    data = json.loads(line)
                    self.save_data(data)
                    if self.tabs.currentIndex() == 1:
                        self.update_data_display(data)
                    elif self.tabs.currentIndex() == 2:
                        self.update_graphs(data)
                    elif self.tabs.currentIndex() == 3:
                        if self.map_checkbox.isChecked():
                            self.update_data_display(data)
                        self.check_map_data_changed()
            except serial.SerialException as e:
                self.show_message("Seri Port Hatası", str(e))
                self.disconnect_serial()
            except json.JSONDecodeError as e:
                pass
            except Exception as e:
                self.show_message("Hata", str(e))

    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
            self.timer.stop()
        self.show_test_mode = True    
        self.window_widget_creator()

    def update_data_display(self, data):
        self.data_entries['name'].setText(data['name'])
        self.data_entries['packageNumber'].setText(str(data['packageNumber']))
        self.data_entries['latitude'].setText(str(data['latitude']))
        self.data_entries['longitude'].setText(str(data['longitude']))
        self.data_entries['speed'].setText(str(data['speed']))
        self.data_entries['pressure'].setText(str(data['pressure']))
        self.data_entries['altitude'].setText(str(data['altitude']))
        self.data_entries['temperature'].setText(str(data['temperature']))
        self.data_entries['pitch'].setText(str(data['pitch']))
        self.data_entries['roll'].setText(str(data['roll']))
        self.data_entries['yaw'].setText(str(data['yaw']))
        self.data_entries['pyroTrigger'].setText(str(data['pyroTrigger']))
        self.data_entries['flightStatus'].setText(str(data['flightStatus']))

    def check_map_data_changed(self):
        latitude = self.data_entries['latitude'].text()
        longitude = self.data_entries['longitude'].text()

        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

            if latitude != self.previous_map_data["latitude"] or longitude != self.previous_map_data["longitude"]:
                self.previous_map_data["latitude"] = latitude
                self.previous_map_data["longitude"] = longitude
                self.update_map(latitude, longitude)

    def update_map(self, latitude, longitude):
        # Harita verilerini güncelle
        if latitude is not None and longitude is not None:
            folium_map = folium.Map(location=[latitude, longitude], zoom_start=17)
            folium.Marker([latitude, longitude], popup=(latitude, longitude)).add_to(folium_map)

            data = io.BytesIO()
            folium_map.save(data, close_file=False)
            self.map_view.setHtml(data.getvalue().decode())

    def open_google_maps(self):
        latitude = self.data_entries['latitude'].text()
        longitude = self.data_entries['longitude'].text()
        url = f"https://www.google.com/maps?q={latitude},{longitude}"
        webbrowser.open(url, new=0)

    def update_graphs(self, data):
        time = datetime.now().strftime("%H:%M:%S")
        self.time_data.append(time)

        self.altitude_data.append(data['altitude'])
        self.pressure_data.append(data['pressure'])
        self.speed_data.append(data['speed'])

        self.altitude_ax.clear()
        self.pressure_ax.clear()
        self.speed_ax.clear()

        self.altitude_ax.plot(self.time_data, self.altitude_data, label="İrtifa")
        self.pressure_ax.plot(self.time_data, self.pressure_data, label="Basınç")
        self.speed_ax.plot(self.time_data, self.speed_data, label="Hız")

        self.altitude_ax.legend(loc='upper left')
        self.pressure_ax.legend(loc='upper left')
        self.speed_ax.legend(loc='upper left')

        self.altitude_ax.set_ylabel("İrtifa (m)")
        self.pressure_ax.set_ylabel("Basınç (hPa)")
        self.speed_ax.set_ylabel("Hız (m/s)")
        self.speed_ax.set_xlabel("Zaman (s)")

        self.altitude_canvas.draw()
        self.pressure_canvas.draw()
        self.speed_canvas.draw()


    def refresh_system_info(self):
        if self.serial_port:
            port_info = f"Port: {self.serial_port.port}\n"
            port_info += f"Baund: {self.serial_port.baudrate}\n"
            port_info += f"Byte: {self.serial_port.bytesize}\n"
            port_info += f"Seri Numarası: {self.serial_port.serial_number if hasattr(self.serial_port, 'serial_number') else 'N/A'}\n"
            self.system_info_text_edit.setPlainText(port_info)
        elif self.test_mode:
            self.system_info_text_edit.setPlainText("Test Modunda Çalışıyor")

    def save_data(self, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_entry = {"time": current_time, "data": data}
        self.data_log.append(data_entry)

    def save_as_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Veri Dosyasını Seç", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        try:
            with open(file_path, "w") as file:
                json.dump(self.data_log, file, indent=4)
        except:
            pass

    def show_message(self, title, message,):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.disconnect_serial()
    sys.exit(app.exec())

# PyInstaller: pyinstaller --noconfirm --onefile --windowed --icon "C:/Users/İrem/Desktop/ground-station_app/resources/icon.ico" --name "Atmaca Roket Takımı - Yer İstasyonu Veri İzleme Aracı"  "C:/Users/İrem/Desktop/ground-station_app/app.py"