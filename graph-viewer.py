import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QFormLayout, QPushButton, QFileDialog, QMessageBox, QToolBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atmaca Roket Takımı - Veri Görüntüleme Aracı")
        self.resize(1200, 800)

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

        self.tabs = QTabWidget()

        # Giriş sekmesi
        self.entry_tab = QWidget()
        self.entry_layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        
        # Yerel HTML dosyasının yolu
        local_html_path = os.path.join(os.path.dirname(__file__), 'resources/entry.html')
        self.web_view.setUrl(QUrl.fromLocalFile(local_html_path))
        
        self.entry_layout.addWidget(self.web_view)
        self.entry_tab.setLayout(self.entry_layout)
        self.tabs.addTab(self.entry_tab, "Giriş")

        # Verileri yükleme düğmesi
        self.load_data_button = QPushButton("Verileri Yükle")
        self.load_data_button.clicked.connect(self.load_data)
        self.entry_layout.addWidget(self.load_data_button)

        self.setCentralWidget(self.tabs)

    def load_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Veri Dosyasını Seç", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.data = json.load(file)
                if self.check_data(self.data):
                    self.create_tabs_for_data()
                else:
                    self.show_message("Hata", "Yüklenen kayıt dosyası bozuk ya da içeriği doğru değil.")
            except Exception as e:
                self.show_message("Hata", f"Veri dosyası yüklenirken hata oluştu: {str(e)}")

    def check_data(self, json_data):
        if isinstance(json_data, list):
            for item in json_data:
                if 'data' in item:
                    data = item['data']
                    required_fields = ['name', 'packageNumber', 'latitude', 'longitude', 'speed',
                                    'pressure', 'altitude', 'temperature', 'pitch', 'roll', 'yaw',
                                    'pyroTrigger', 'flightStatus']
                    for field in required_fields:
                        if field not in data:
                            return False
                else:
                    return False
            return True
        else:
            return False

    def create_tabs_for_data(self):
        data_keys = self.data[0]['data'].keys()
        
        for key in data_keys:
            tab = QWidget()
            layout = QVBoxLayout()
            figure, ax = plt.subplots()
            canvas = FigureCanvas(figure)
            toolbar = NavigationToolbar2QT(canvas, self)

            times = [entry['time'] for entry in self.data]
            values = [entry['data'][key] for entry in self.data]

            if key in ["latitude", "longitude", "speed"]:
                values = list(map(float, values))

            ax.plot(times, values)
            ax.set_title(key.capitalize())
            ax.set_xlabel("Time")
            ax.set_ylabel(key.capitalize())

            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            tab.setLayout(layout)
            self.tabs.addTab(tab, key.capitalize())

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
