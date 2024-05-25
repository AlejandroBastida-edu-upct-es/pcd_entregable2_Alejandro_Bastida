from datetime import datetime
import time
import random
from statistics import mean, stdev

# Patrón Singleton
class SistemaIOT:
    _instancia = None

    @classmethod
    def obtener_instancia(cls):
        if cls._instancia is None:
            cls._instancia = SistemaIOT()
        return cls._instancia

# Patrón Observer
class Sujeto:
    def __init__(self):
        self.observadores = []

    def añadir_observador(self, observador):
        self.observadores.append(observador)

    def notificar_observadores(self, datos):
        for observador in self.observadores:
            observador.actualizar(datos)

class Observador:
    def actualizar(self, datos):
        pass

class SistemaSensorTemperatura(Sujeto):
    def __init__(self):
        super().__init__()

class Sensor:
    def __init__(self, sistema):
        self.sistema = sistema

    def enviar_temperatura(self, marca_tiempo, temperatura):
        datos = {'marca_tiempo': marca_tiempo, 'temperatura': temperatura}
        self.sistema.notificar_observadores(datos)

class ProcesadorDatos(Observador):
    def __init__(self, cadena):
        self.cadena = cadena

    def actualizar(self, datos):
        self.cadena.manejar(datos)

# Patrón cadena of Responsibility
class Manejador:
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    def manejar(self, datos):
        if self.sucesor:
            self.sucesor.manejar(datos)

class ManejadorEstadisticos(Manejador):
    def __init__(self, calculador_estadisticos, sucesor=None):
        super().__init__(sucesor)
        self.calculador_estadisticos = calculador_estadisticos
        self.conjunto_de_datos = []

    def manejar(self, datos):
        self.conjunto_de_datos.append(datos)
        ahora = datetime.now().timestamp()
        # datos de los últimos 60 segundos
        self.conjunto_de_datos = list(filter(lambda x: x['marca_tiempo'].timestamp() >= ahora - 60, self.conjunto_de_datos))
        estadisticas = self.calculador_estadisticos.calcular(self.conjunto_de_datos)
        print(f"Estadísticas: {estadisticas}")
        super().manejar(datos)

class ManejadorUmbral(Manejador):
    def __init__(self, umbral, sucesor=None):
        super().__init__(sucesor)
        self.umbral = umbral

    def manejar(self, datos):
        if datos['temperatura'] > self.umbral:
            print("Alerta: La temperatura está por encima del umbral")
        super().manejar(datos)

class ManejadorIncremento(Manejador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.conjunto_de_datos = []

    def manejar(self, datos):
        self.conjunto_de_datos.append(datos)
        ahora = datetime.now().timestamp()
        # datos de los últimos 30 segundos
        self.conjunto_de_datos = list(filter(lambda x: x['marca_tiempo'].timestamp() >= ahora - 30, self.conjunto_de_datos))
        if len(self.conjunto_de_datos) > 1:
            incremento_de_temperatura = datos['temperatura'] - self.conjunto_de_datos[0]['temperatura']
            if incremento_de_temperatura > 10:
                print("Alerta: La temperatura ha aumentado más de 10 grados en los últimos 30 segundos")
        super().manejar(datos)

# Patrón Strategy
class Estrategia:
    def calcular(self, datos):
        pass

class EstrategiaMediaDesviacion(Estrategia):
    def calcular(self, datos):
        temperaturas = list(map(lambda x: x['temperatura'], datos))
        if len(temperaturas) > 1:
            return {'media': mean(temperaturas), 'desviacion_estandar': stdev(temperaturas)}
        else:
            return {'media': temperaturas[0], 'desviacion_estandar': 0}

class EstrategiaCuantiles(Estrategia):
    def calcular(self, datos):
        temperaturas = list(map(lambda x: x['temperatura'], datos))
        return {'cuantiles': self._calcular_cuantiles(temperaturas)}

    def _calcular_cuantiles(self, datos):
        datos_ordenados = sorted(datos)
        return {'q1': datos_ordenados[int(len(datos_ordenados) * 0.25)], 'mediana': datos_ordenados[int(len(datos_ordenados) * 0.5)], 'q3': datos_ordenados[int(len(datos_ordenados) * 0.75)]}

class EstrategiaMaxMin(Estrategia):
    def calcular(self, datos):
        temperaturas = list(map(lambda x: x['temperatura'], datos))
        return {'min': min(temperaturas), 'max': max(temperaturas)}

class CalculadorEstadisticos:
    def __init__(self, estrategia):
        self.estrategia = estrategia

    def escoger_estrategia(self, estrategia):
        self.estrategia = estrategia

    def calcular(self, datos):
        return self.estrategia.calcular(datos)


if __name__ == "__main__":
    # sistema IoT (Singletomn)
    sistema_iot = SistemaIOT.obtener_instancia()

    # sistema de sensor de temperatura (Sujeto)
    sistema_sensor_temperatura = SistemaSensorTemperatura()

    # cadena de responsabilidad
    calculador_estadisticos = CalculadorEstadisticos(EstrategiaMediaDesviacion())
    manejador_incremento = ManejadorIncremento()
    manejador_umbral = ManejadorUmbral(umbral=30, sucesor=manejador_incremento)
    manejador_estadisticos = ManejadorEstadisticos(calculador_estadisticos, sucesor=manejador_umbral)

    procesador_datos = ProcesadorDatos(manejador_estadisticos)
    sistema_sensor_temperatura.añadir_observador(procesador_datos)

    # envío de dfatos de temperatura del sensor
    sensor = Sensor(sistema_sensor_temperatura)

    while True:
        marca_tiempo = datetime.now()
        temperatura = random.uniform(15.0, 35.0)  # valor de temperatura aleatorio
        sensor.enviar_temperatura(marca_tiempo, temperatura)
        time.sleep(5)
