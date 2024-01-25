import csv
import cv2
import torch
from ultralytics import YOLO
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import folium
from math import radians, sin, cos, sqrt, atan2

class ObjectDetection:
    def __init__(self, capture_index, csv_path, map_html_path):
        self.capture_index = capture_index
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model()
        self.csv_path = csv_path
        self.load_csv()
        self.map_html_path = map_html_path
        self.coordenadas_visitadas = []
        self.last_time = datetime.now()
        self.dupli = []

    def load_model(self):
        model = YOLO("weights/best90.pt")  
        model.fuse()
        return model

    def predict(self, frame):
        results = self.model(frame)
        return results

    def load_csv(self):
        self.object_data = []
        with open(self.csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # saltar la primera linea, que es la de las cabeceras
            for row in csv_reader:
                self.object_data.append({'ID': int(row[2]), 'Longitude': float(row[0]), 'Latitude': float(row[1])})

    def find_object_in_csv(self, object_id):
        for obj in self.object_data:

            if object_id in self.dupli:
                print(f"Duplicado del: {object_id}")
                return None
                
            if obj['ID'] == object_id:
                self.dupli.append(object_id)
                return obj
        return None

    def plot_boxes(self, frame, results):
        xyxys = []

        for result in results:
            boxes = result.boxes.cpu().numpy()
            xyxyss = boxes.xyxy

            for xyxy in xyxyss:
                centro_x = (int(xyxy[0]) + int(xyxy[2])) / 2
                centro_y = (int(xyxy[1]) + int(xyxy[3])) / 2

                # comprobar si está en el csv
                object_id = int(boxes.cls)
                object_info = self.find_object_in_csv(object_id)

                if object_info:
                    print(f"Object ID: {object_id}, Longitude: {object_info['Longitude']}, Latitude: {object_info['Latitude']}")
                    self.update_map(object_info['Longitude'], object_info['Latitude'])
                else:
                    print(f"Object ID: {object_id}, Not found in CSV")

    def update_map(self, lat, lon):
        if self.last_time:
            current_time = datetime.now()
            time_diff = (current_time - self.last_time).seconds
            speed = self.calculate_speed(lat, lon, time_diff)
            print(f"Velocidad: {speed} km/h")

        self.coordenadas_visitadas.append((lat, lon))
        self.last_time = datetime.now()

        mapa = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup='Ubicación').add_to(mapa)
        folium.PolyLine(locations=self.coordenadas_visitadas, color='blue', popup=self.coordenadas_visitadas).add_to(mapa)

        mapa.save(self.map_html_path)

    def calculate_speed(self, lat, lon, time_diff):
        prev_lat, prev_lon = self.coordenadas_visitadas[-1] if self.coordenadas_visitadas else (lat, lon)
        distancia = self.calculate_distance(prev_lat, prev_lon, lat, lon)

        if time_diff != 0 and distancia != 0:
            velocidad = distancia / (time_diff / 3600)
            return velocidad
        else:
            return 0
        
        

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        radio_tierra = 6371.0

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distancia = radio_tierra * c

        return distancia

    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened(), "Cannot open camera"

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = self.predict(frame)
            #final = self.plot_boxes(frame, results)
            self.plot_boxes(frame, results)

            key = cv2.waitKey(1)
            
            #cv2.imshow('Exacto', final)
            if key & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


def main():
    obj_detection = ObjectDetection(capture_index=0, csv_path='DB/Almacen/coordenadas.csv', map_html_path='DB/Almacen/mapa_objetos.html')
    obj_detection()



if __name__ == '__main__':
    main()
