import pytest
from datetime import datetime
from entregable2_PPCD_prueba import SistemaIOT, SistemaSensorTemperatura, Sensor, ProcesadorDatos, ManejadorEstadisticos, ManejadorUmbral, ManejadorIncremento, EstrategiaMediaDesviacion, CalculadorEstadisticos

def test_singleton():
    instance1 = SistemaIOT.obtener_instancia()
    instance2 = SistemaIOT.obtener_instancia()
    assert instance1 is instance2

def test_observer():
    sistema_sensor_temperatura = SistemaSensorTemperatura()
    procesador_datos = ProcesadorDatos(None)
    sistema_sensor_temperatura.añadir_observador(procesador_datos)
    assert len(sistema_sensor_temperatura.observadores) == 1

def test_cadenaderesponsabilidad():
    estrategia = EstrategiaMediaDesviacion()
    calculador_estadisticos = CalculadorEstadisticos(estrategia)
    manejador_incremento = ManejadorIncremento()  
    manejador_umbral = ManejadorUmbral(umbral=30, sucesor=manejador_incremento)
    manejador_estadisticos = ManejadorEstadisticos(calculador_estadisticos, sucesor=manejador_umbral)   
    datos = [{'marca_tiempo': datetime.now(), 'temperatura': 32}, {'marca_tiempo': datetime.now(), 'temperatura': 28}]
    manejador_estadisticos.manejar(datos[0])
    manejador_estadisticos.manejar(datos[1])

    estadisticas = estrategia.calcular(datos)
    assert estadisticas['media'] == 30  
    assert estadisticas['desviacion_estandar'] == pytest.approx(2, abs=1)  # Desviación estándar aproximada

def test_estrategia():
    calculador_estadisticos = CalculadorEstadisticos(EstrategiaMediaDesviacion())
    datos = [{'marca_tiempo': datetime.now(), 'temperatura': 25}, {'marca_tiempo': datetime.now(), 'temperatura': 30}]
    estadisticas = calculador_estadisticos.calcular(datos)
    assert 'media' in estadisticas
