from datetime import datetime
import time
import random
from statistics import mean, stdev

# Patrón Singleton, aqui unicamente tenemos la funcion obtener_instancia donde nos devuelve la unica instancia del singleton.
class SistemaIOT:
    _instancia = None

    @classmethod
    def obtener_instancia(cls):
        if cls._instancia is None:
            cls._instancia = SistemaIOT()
        return cls._instancia

# Patrón Observer, aqui nos resulta de mucha ayuda la estructura del patron ya qeu practicvamente implementamos
# las funciones tal cual estan definidas en el patron incluyendo modificaciones.
class Sujeto:
    # iniciamos una lista vacia para almacenar observadores
    def __init__(self):
        self.observadores = []

    # los añadimos a la lista.
    def añadir_observador(self, observador):
        self.observadores.append(observador)

    # notifica a los observadores con los datos proporcionados por 
    # si ocurre una excepcion la levanta.
    def notificar_observadores(self, datos):
        for observador in self.observadores:
            try:
                observador.actualizar(datos)
            except Exception as e:
                raise Exception(f"Error al notificar al observador: {e}")

class Observador:
    def actualizar(self, datos):
        pass

class SistemaSensorTemperatura(Sujeto):
    def __init__(self):
        super().__init__()

# la clase sensor tiene un constructor que toma un sistema como parametro.
class Sensor:
    def __init__(self, sistema):
        self.sistema = sistema

    # esta funcion crea un diccionario de datos con las marcas de tiempo y temperatura y notifica a los observadores del sistema.
    # si ocurre una expcepcion la levanta.
    def enviar_temperatura(self, marca_tiempo, temperatura):
        datos = {'marca_tiempo': marca_tiempo, 'temperatura': temperatura}
        try:
            self.sistema.notificar_observadores(datos)
        except Exception as e:
            raise Exception(f"Error al enviar temperatura: {e}")

# la clase procesador de datos toma una cadena de responsabilidad definida previamente.
class ProcesadorDatos(Observador):
    def __init__(self, cadena):
        self.cadena = cadena

    # esta funcion maneja los datos acorde con la caden ade responsabilidad.
    def actualizar(self, datos):
        try:
            self.cadena.manejar(datos)
        except Exception as e:
            raise Exception(f"Error al procesar datos: {e}")

# Patrón cadena de responsabilidad, al igual que en diagrama del patron definimos un atributo sucesor para que el usuario nos notifique quien debe tramitar la "solicitud"
class Manejador:
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    def manejar(self, datos):
        if self.sucesor:
            self.sucesor.manejar(datos)

# esta clase toma como parametros el conjunto de estadisticos y el conjunto de datos.
class ManejadorEstadisticos(Manejador):
    def __init__(self, calculador_estadisticos, sucesor=None):
        super().__init__(sucesor)
        self.calculador_estadisticos = calculador_estadisticos
        self.conjunto_de_datos = []

    # esta funcion añade los datos y filtra para mantener unicamente los datos de los ultimos 60 segundos. 
    def manejar(self, datos):
        self.conjunto_de_datos.append(datos)
        ahora = datetime.now().timestamp()
        self.conjunto_de_datos = list(filter(lambda x: x['marca_tiempo'].timestamp() >= ahora - 60, self.conjunto_de_datos))
        try:
            estadisticas = self.calculador_estadisticos.calcular(self.conjunto_de_datos)
            print(f"Estadísticas: {estadisticas}")
        except Exception as e:
            raise Exception(f"Error al calcular estadísticas: {e}")
        super().manejar(datos)

# la clase necesaria para manejar el umbral establecido por usuario.
class ManejadorUmbral(Manejador):
    def __init__(self, umbral, sucesor=None):
        super().__init__(sucesor)
        self.umbral = umbral

    # esta parte compruueba si la temepratura supera el umbral .
    def manejar(self, datos):
        try:
            if datos['temperatura'] > self.umbral:
                print("Alerta: La temperatura está por encima del umbral")
        except Exception as e:
            raise Exception(f"Error al comprobar umbral: {e}")
        super().manejar(datos)

# clase para tratar el incremento de temperatura, para ello le tenemos que pasar el conjunto de datos.
class ManejadorIncremento(Manejador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.conjunto_de_datos = []

    # este codigo añade los datos y filtra para obtener los de los ultimos 30 segundos, calcula el incremento de temperatura y notifica al sistema si es mayor a 10 grados.
    def manejar(self, datos):
        self.conjunto_de_datos.append(datos)
        ahora = datetime.now().timestamp()
        self.conjunto_de_datos = list(filter(lambda x: x['marca_tiempo'].timestamp() >= ahora - 30, self.conjunto_de_datos))
        try:
            if len(self.conjunto_de_datos) > 1:
                incremento_de_temperatura = datos['temperatura'] - self.conjunto_de_datos[0]['temperatura']
                if incremento_de_temperatura > 10:
                    print("Alerta: La temperatura ha aumentado más de 10 grados en los últimos 30 segundos")
        except Exception as e:
            raise Exception(f"Error al comprobar incremento de temperatura: {e}")
        super().manejar(datos)

# Patrón Strategyn, aqui tal y como nos dice el enunciado necesitamos una serie de estrategias para el calculo de diferentes estadisticos, para ello lo mas
# correcto era usar el patron strategy.
class Estrategia:
    def calcular(self, datos):
        pass


# estas clases son unicamente funciones en las que definimos el calculo de diferentes estadisticos y guardamos estas estadisticas para pasarlas al manejador.
# y ya segun la estrategia que el usuario dese calcular se pasa a una variable estrategia de la cual se calculann los valores a partir de las etsrategias.
class EstrategiaMediaDesviacion(Estrategia):
    def calcular(self, datos):
        temperaturas = list(map(lambda x: x['temperatura'], datos))
        if len(temperaturas) > 1:
            estadisticas = {'media': mean(temperaturas), 'desviacion_estandar': stdev(temperaturas)}
            return estadisticas
        else:
            estadisticas = {'media': temperaturas[0], 'desviacion_estandar': 0}
            return estadisticas
        
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

# Sección principal
if __name__ == "__main__":
    # sistema IoT (Singleton)
    sistemaiot = SistemaIOT.obtener_instancia()

    # sistema del sensor de temperatura (Sujeto)
    sensor_temperatura = SistemaSensorTemperatura()

    # cadena de responsabilidad
    calculador_estadisticos = CalculadorEstadisticos(EstrategiaMediaDesviacion())
    manejador_incremento = ManejadorIncremento()
    manejador_umbral = ManejadorUmbral(umbral=30, sucesor=manejador_incremento)
    manejador_estadisticos = ManejadorEstadisticos(calculador_estadisticos, sucesor=manejador_umbral)

    procesador_datos = ProcesadorDatos(manejador_estadisticos)
    sensor_temperatura.añadir_observador(procesador_datos)

    # envío de datos de temperatura desde el sensor
    sensor = Sensor(sensor_temperatura)

    while True:
        marca_tiempo = datetime.now()
        temperatura = random.uniform(15.0, 35.0)  # valor de temperatura aleatorio
        sensor.enviar_temperatura(marca_tiempo, temperatura)
        time.sleep(5)
