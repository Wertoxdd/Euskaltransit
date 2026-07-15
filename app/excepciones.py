class ErrorTransporteBase(Exception):
    # Excepción base
    pass

class ArchivoGTFSNoEncontradoError(ErrorTransporteBase):
    # Por si falta un .txt esencial
    def __init__(self, archivo_nombre: str):
        self.message = f"Error crítico: No se pudo encontrar el archivo GTFS requerido: {archivo_nombre}"
        super().__init__(self.message)

class CoordenadaInvalidaError(ErrorTransporteBase):
    def __init__(self):
        self.message = f"Error crítico: Coordenadas invalidas"
        super().__init__(self.message)
