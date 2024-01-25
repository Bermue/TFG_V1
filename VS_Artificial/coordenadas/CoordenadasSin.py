from datetime import datetime
import sys
import folium
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from PyQt5.QtCore import QUrl
from math import radians, sin, cos, sqrt, atan2

class variables:
    velocidades = []

class VentanaMapa(QMainWindow):
    def __init__(self, lat, lon):
        super().__init__()

        self.setWindowTitle("Mapa")
        self.setGeometry(100, 100, 800, 600)

        self.mapa = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup='Ubicación').add_to(self.mapa)
        ruta_mapa_html = '/Users/carlitosb/Documents/TFG_V2/DB/Almacen/mapa.html'  
        self.mapa.save(ruta_mapa_html)

        self.browser = QWebEngineView(self)
        self.browser.setGeometry(0, 0, 800, 600)
        self.browser.setUrl(QUrl.fromLocalFile(ruta_mapa_html))

        self.setCentralWidget(QWidget(self))
        layout = QVBoxLayout(self.centralWidget())

        self.btn_cerrar = QPushButton('Cerrar Mapa', self)
        self.btn_cerrar.clicked.connect(self.close)
        layout.addWidget(self.browser)
        layout.addWidget(self.btn_cerrar)

class VentanaMapaRegistros(QMainWindow):
    def __init__(self, coordenadas_visitadas):
        super().__init__()

        self.setWindowTitle("Mapa de Registros")
        self.setGeometry(100, 100, 800, 600)

        initial_coords = coordenadas_visitadas[0] if coordenadas_visitadas else [40.416775, -3.70379]
        self.mapa = folium.Map(location=initial_coords, zoom_start=15)

        for coords in coordenadas_visitadas:
            folium.Marker(coords, popup='Ubicación').add_to(self.mapa)

        folium.PolyLine(locations=coordenadas_visitadas, color='blue').add_to(self.mapa)

        ruta_mapa_html = '/Users/carlitosb/Documents/TFG_V2/DB/Almacen/mapa_registros.html'
        self.mapa.save(ruta_mapa_html)

        self.browser = QWebEngineView(self)
        self.browser.setGeometry(0, 0, 800, 600)
        self.browser.setUrl(QUrl.fromLocalFile(ruta_mapa_html))

        self.setCentralWidget(QWidget(self))
        layout = QVBoxLayout(self.centralWidget())

        self.btn_cerrar = QPushButton('Cerrar Mapa de Registros', self)
        self.btn_cerrar.clicked.connect(self.close)
        layout.addWidget(self.browser)
        layout.addWidget(self.btn_cerrar)




class VentanaCoordenadas(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.setWindowTitle("Buscar Coordenadas por ID")
        self.setGeometry(200, 200, 400, 300)

        self.lbl_id = QLabel("Introducir ID:", self)
        layout.addWidget(self.lbl_id)

        self.txt_id = QLineEdit(self)
        layout.addWidget(self.txt_id)

        self.btn_mostrar_mapa = QPushButton("Mostrar Mapa", self)
        self.btn_mostrar_mapa.clicked.connect(self.mostrar_mapa)
        layout.addWidget(self.btn_mostrar_mapa)

        self.btn_mostrar_registros = QPushButton("Mostrar Registros", self)
        self.btn_mostrar_registros.clicked.connect(self.mostrar_registros)
        layout.addWidget(self.btn_mostrar_registros)

        self.setLayout(layout)

        self.df = pd.read_csv('/Users/carlitosb/Documents/TFG_V2/DB/Almacen/coordenadas.csv')
        self.coordenadas_visitadas = []
        self.last_time = None

    def mostrar_mapa(self):
        input_id = int(self.txt_id.text())

        row = self.df[self.df['ID'] == input_id]

        if not row.empty:
            lat = float(row['Latitud'].iloc[0]) 
            lon = float(row['Longitud'].iloc[0])

            if self.last_time:
                current_time = datetime.now()
                time_diff = (current_time - self.last_time).seconds
                speed = self.calcular_velocidad(lat, lon, time_diff)
                variables.velocidades.append(speed)
                print(f"Velocidad: {speed} km/h")

            self.coordenadas_visitadas.append((lat, lon))
            self.ventana_mapa = VentanaMapa(lat, lon)
            self.ventana_mapa.show()

            self.last_time = datetime.now()

    def calcular_velocidad(self, lat, lon, time_diff):
        prev_lat, prev_lon = self.coordenadas_visitadas[-1] if self.coordenadas_visitadas else (lat, lon)
        distancia = self.calcular_distancia(prev_lat, prev_lon, lat, lon)

        velocidad = distancia / (time_diff / 3600)
        return velocidad

    @staticmethod
    def calcular_distancia(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        radio_tierra = 6371.0

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distancia = radio_tierra * c

        return distancia

    def mostrar_registros(self):
        mapa_coordenadas = folium.Map(location=[40.416775, -3.70379], zoom_start=10)

        total_distance = 0  
        total_time = 0  
        num_segments = len(self.coordenadas_visitadas) - 1 


        for i in range(num_segments):
            lat1, lon1 = self.coordenadas_visitadas[i]
            lat2, lon2 = self.coordenadas_visitadas[i + 1]

            distancia = self.calcular_distancia(lat1, lon1, lat2, lon2)
            total_distance += distancia

            tiempo_segmento = (datetime.now() - self.last_time).seconds
            total_time += tiempo_segmento

            self.last_time = datetime.now()

            # Dibujar una línea entre las coordenadas
            folium.PolyLine(locations=[(lat1, lon1), (lat2, lon2)], color='blue').add_to(mapa_coordenadas)

        if num_segments > 0:
            velocidad_media_de_medias = sum(variables.velocidades) / len(variables.velocidades)
            print(f"Velocidad media: {velocidad_media_de_medias} km/h")


        for coords in self.coordenadas_visitadas:
            folium.Marker(coords, popup='Ubicación').add_to(mapa_coordenadas)

        ruta_mapa_html = '/Users/carlitosb/Documents/TFG_V2/DB/Almacen/mapa_registros.html'
        mapa_coordenadas.save(ruta_mapa_html)

        self.ventana_mapa_registros = VentanaMapaRegistros(self.coordenadas_visitadas)
        self.ventana_mapa_registros.show()


def main():
    app = QApplication(sys.argv)
    ventana_coordenadas = VentanaCoordenadas()
    ventana_coordenadas.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()