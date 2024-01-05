
# menu
# Menú encargado de abrir los demás archivos .py y unificar todo en el mismo programa

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from typing import Any
import cv2
import torch
from ultralytics import YOLO
import numpy as np
from time import time
from Calibrado import variables
from Calibrado import MainWindow2



def funcion1():
    exec(open('VS_Artificial/Calibrado.py').read())
       

def funcion2():
    exec(open('VS_Artificial/VS_AR.py').read())

def funcion3():
    exec(open('VS_Artificial/VS_ARFoto.py').read())

def funcion4():
    exec(open('VS_Artificial/VS_ARVideo.py').read())

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Menú de Selección')
        self.setGeometry(100, 100, 300, 200)
        distancia_focal = self.leer_distancia_focal()


        layout = QVBoxLayout()

        self.actualizar = QPushButton('Actualizar')
        self.actualizar.clicked.connect(self.actualizar_texto_calibracion)
        layout.addWidget(self.actualizar)


        self.label = QLabel()
        self.actualizar_texto_calibracion() 
        layout.addWidget(self.label)


        button1 = QPushButton('Calibrado', self)
        button1.clicked.connect(funcion1)
        button1.clicked.connect(self.abrir_ventana_Calibrado)
        layout.addWidget(button1)

        button2 = QPushButton('Live', self)
        button2.clicked.connect(funcion2)
        layout.addWidget(button2)

        button3 = QPushButton('Foto', self)
        button3.clicked.connect(funcion3)
        layout.addWidget(button3)

        button4 = QPushButton('Video', self)
        button4.clicked.connect(funcion4)
        layout.addWidget(button4)

        self.setLayout(layout)

    def abrir_ventana_Calibrado(self):
        self.archivo1_window = MainWindow2()  # Crear una instancia de la ventana de archivo1
        self.archivo1_window.show()  # Mostrar la ventana de archivo1

    def leer_distancia_focal(self):
        try:
            nombre_archivo = 'VS_Artificial/distanciaFocal.txt'
            with open(nombre_archivo, 'r') as archivo:
                lineas = archivo.readlines()
                if lineas:
                    ultimo_numero = float(lineas[-1].strip())  # Convertir el último número a flotante
                    return ultimo_numero
                else:
                    return None
        except (FileNotFoundError, ValueError):
            return None
        
    def actualizar_texto_calibracion(self):
        distancia_focal = self.leer_distancia_focal()
        if distancia_focal is not None:
            texto = f"Calibración actual: {distancia_focal}"
            self.label.setText(texto)
            self.label.setStyleSheet("")  # Limpia cualquier estilo existente
        else:
            texto = "Calibración: Pendiente"
            self.label.setText(texto)
            self.label.setStyleSheet("color: red")  # Texto en rojo


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.show()
    sys.exit(app.exec_())
