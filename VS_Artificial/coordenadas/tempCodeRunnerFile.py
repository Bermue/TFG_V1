    def calcular_velocidad(self, lat, lon, time_diff):
        prev_lat, prev_lon = self.coordenadas_visitadas[-1] if self.coordenadas_visitadas else (lat, lon)
        distancia = self.calcular_distancia(prev_lat, prev_lon, lat, lon)

        velocidad = distancia / (time_diff / 3600)
        return velocidad