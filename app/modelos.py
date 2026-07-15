from app.excepciones import ErrorTransporteBase 

class Estacion:
    def __init__(self, id_estacion: str, nombre: str, latitud: float, longitud: float):
        self.id = id_estacion
        self.nombre = nombre

        if not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
            raise ValueError(f"Coordenadas fuera de rango para la estación {nombre}")

        self.latitud = latitud
        self.longitud = longitud
        self.lineas = []

    def agregar_linea(self, linea: str):
        if linea not in self.lineas:
            self.lineas.append(linea)

    def __repr__(self):
        return f"<Estación {self.nombre} ({self.id})>"
    
class Linea:
    def __init__(self, id_linea: str, nombre_corto: str, color_hex: str):
        self.id = id_linea
        self.nombre = nombre_corto
        self.color = color_hex

        self.estaciones = []
    
    def __repr__(self):
        return f"<Linea {self.nombre} (Estaciones: {len(self.estaciones)})>"
    
    def agregar_estacion(self, estacion):
        if not any(e.id == estacion.id for e in self.estaciones):
            self.estaciones.append(estacion)
        else:
            print(f"Aviso: La estacion {estacion.id} ya existe en la {self.nombre}.")