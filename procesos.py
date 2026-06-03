"""
procesos.py - Módulo de Planificación de Procesos
===================================================
Proyecto: Simulador de Sistema Operativo - 2026-1
Integrante 1: Planificación de Procesos
Universidad Pedagógica y Tecnológica de Colombia (UPTC)

Responsabilidades:
    - Estructura de datos de los procesos
    - Cola de procesos
    - Algoritmos: Round Robin y Prioridad
    - Métricas: tiempo de espera, tiempo de ejecución, tiempo de retorno
    - Estadísticas y reportes
"""

from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional
import time


# =============================================================================
# ESTRUCTURA DE DATOS: PROCESO
# =============================================================================

# Estados posibles de un proceso
ESTADO_NUEVO       = "NUEVO"
ESTADO_LISTO       = "LISTO"
ESTADO_EJECUTANDO  = "EJECUTANDO"
ESTADO_TERMINADO   = "TERMINADO"

@dataclass
class Proceso:
    """
    Representa un proceso simulado dentro del sistema operativo.

    Atributos:
        pid          (int)  : Identificador único del proceso.
        nombre       (str)  : Nombre descriptivo del proceso.
        duracion     (int)  : Tiempo total de CPU que necesita (ráfaga, en unidades de tiempo).
        prioridad    (int)  : Prioridad del proceso (menor número = mayor prioridad).
        tiempo_llegada (int): Instante en que el proceso llega a la cola de listos.
        uso_cpu      (float): Porcentaje de uso de CPU simulado (0.0 - 100.0).
        acceso_archivos (bool): Indica si el proceso requiere acceso a archivos.

        # Campos internos (calculados durante la simulación)
        estado            : Estado actual del proceso.
        tiempo_restante   : Ráfaga que aún falta ejecutar.
        tiempo_inicio     : Instante en que el proceso comenzó su primera ejecución.
        tiempo_fin        : Instante en que el proceso terminó.
        tiempo_espera     : Tiempo total que esperó en la cola de listos.
        tiempo_ejecucion  : Tiempo total que estuvo en la CPU.
        tiempo_retorno    : tiempo_fin - tiempo_llegada (turnaround time).
    """
    pid              : int
    nombre           : str
    duracion         : int
    prioridad        : int         = 0
    tiempo_llegada   : int         = 0
    uso_cpu          : float       = 0.0
    acceso_archivos  : bool        = False

    # Campos internos — no se pasan al crear el proceso
    estado           : str         = field(default=ESTADO_NUEVO, init=False)
    tiempo_restante  : int         = field(default=0,            init=False)
    tiempo_inicio    : Optional[int] = field(default=None,       init=False)
    tiempo_fin       : Optional[int] = field(default=None,       init=False)
    tiempo_espera    : int         = field(default=0,            init=False)
    tiempo_ejecucion : int         = field(default=0,            init=False)
    tiempo_retorno   : int         = field(default=0,            init=False)

    def __post_init__(self):
        # Al crearse, la ráfaga restante es igual a la duración total
        self.tiempo_restante = self.duracion

    def __str__(self):
        return (
            f"Proceso(pid={self.pid}, nombre='{self.nombre}', "
            f"duracion={self.duracion}, prioridad={self.prioridad}, "
            f"llegada={self.tiempo_llegada}, estado={self.estado})"
        )


# =============================================================================
# COLA DE PROCESOS
# =============================================================================

class ColaProcesos:
    """
    Gestiona la cola de procesos listos para ser ejecutados.

    Internamente usa un deque para operaciones O(1) en ambos extremos.
    Permite agregar, quitar y consultar procesos de forma sencilla.
    """

    def __init__(self):
        self._cola: deque = deque()

    def agregar(self, proceso: Proceso) -> None:
        """Agrega un proceso al final de la cola y lo marca como LISTO."""
        proceso.estado = ESTADO_LISTO
        self._cola.append(proceso)

    def quitar_frente(self) -> Optional[Proceso]:
        """Extrae y devuelve el proceso del frente de la cola. None si está vacía."""
        if self._cola:
            return self._cola.popleft()
        return None

    def esta_vacia(self) -> bool:
        """Devuelve True si la cola no tiene procesos."""
        return len(self._cola) == 0

    def tamanio(self) -> int:
        """Número de procesos actualmente en la cola."""
        return len(self._cola)

    def ver_cola(self) -> List[Proceso]:
        """Devuelve una lista (copia) de los procesos en la cola, en orden."""
        return list(self._cola)

    def __repr__(self):
        nombres = [f"P{p.pid}" for p in self._cola]
        return f"ColaProcesos([{' -> '.join(nombres)}])"


# =============================================================================
# ALGORITMO 1: ROUND ROBIN
# =============================================================================

def round_robin(procesos: List[Proceso], quantum: int = 2) -> List[dict]:
    """
    Simula la planificación Round Robin con un quantum de tiempo dado.

    Cada proceso recibe como máximo `quantum` unidades de CPU por turno.
    Si no termina, vuelve al final de la cola.

    Parámetros:
        procesos (List[Proceso]): Lista de procesos a planificar.
        quantum  (int)          : Quantum de tiempo (por defecto 2).

    Retorna:
        List[dict]: Registro de ejecución con entradas del tipo
                    {'pid', 'nombre', 'inicio', 'fin', 'duracion_turno'}.
    """
    # Reiniciar métricas para no acumular si se llama varias veces
    for p in procesos:
        p.tiempo_restante  = p.duracion
        p.estado           = ESTADO_NUEVO
        p.tiempo_inicio    = None
        p.tiempo_fin       = None
        p.tiempo_espera    = 0
        p.tiempo_ejecucion = 0
        p.tiempo_retorno   = 0

    # Ordenar por tiempo de llegada
    cola = deque(sorted(procesos, key=lambda p: p.tiempo_llegada))
    tiempo_actual = 0
    registro = []         # Línea de tiempo de ejecución
    listos: deque = deque()

    # Mover a la cola de listos los que llegan en t=0
    while cola and cola[0].tiempo_llegada <= tiempo_actual:
        p = cola.popleft()
        p.estado = ESTADO_LISTO
        listos.append(p)

    while listos or cola:
        if not listos:
            # La CPU queda ociosa hasta que llegue el siguiente proceso
            tiempo_actual = cola[0].tiempo_llegada
            while cola and cola[0].tiempo_llegada <= tiempo_actual:
                p = cola.popleft()
                p.estado = ESTADO_LISTO
                listos.append(p)

        proceso = listos.popleft()
        proceso.estado = ESTADO_EJECUTANDO

        # Primera vez en CPU
        if proceso.tiempo_inicio is None:
            proceso.tiempo_inicio = tiempo_actual

        # Tiempo que realmente ejecutará en este turno
        turno = min(quantum, proceso.tiempo_restante)
        inicio_turno = tiempo_actual
        tiempo_actual += turno
        proceso.tiempo_restante  -= turno
        proceso.tiempo_ejecucion += turno

        registro.append({
            "pid"          : proceso.pid,
            "nombre"       : proceso.nombre,
            "inicio"       : inicio_turno,
            "fin"          : tiempo_actual,
            "duracion_turno": turno
        })

        # Llegan nuevos procesos durante este turno
        while cola and cola[0].tiempo_llegada <= tiempo_actual:
            p = cola.popleft()
            p.estado = ESTADO_LISTO
            listos.append(p)

        if proceso.tiempo_restante == 0:
            proceso.estado       = ESTADO_TERMINADO
            proceso.tiempo_fin   = tiempo_actual
            proceso.tiempo_retorno = proceso.tiempo_fin - proceso.tiempo_llegada
            proceso.tiempo_espera  = proceso.tiempo_retorno - proceso.duracion
        else:
            proceso.estado = ESTADO_LISTO
            listos.append(proceso)   # Vuelve al final de la cola

    return registro


# =============================================================================
# ALGORITMO 2: PLANIFICACIÓN POR PRIORIDAD (no expulsivo)
# =============================================================================

def planificacion_prioridad(procesos: List[Proceso]) -> List[dict]:
    """
    Simula la planificación por Prioridad en modo NO expulsivo (non-preemptive).

    En cada instante en que la CPU queda libre, se elige el proceso listo
    con mayor prioridad (menor valor numérico). Si hay empate en prioridad,
    se desempata por tiempo de llegada (FCFS).

    Parámetros:
        procesos (List[Proceso]): Lista de procesos a planificar.

    Retorna:
        List[dict]: Registro de ejecución con entradas del tipo
                    {'pid', 'nombre', 'inicio', 'fin', 'duracion_turno'}.
    """
    # Reiniciar métricas
    for p in procesos:
        p.tiempo_restante  = p.duracion
        p.estado           = ESTADO_NUEVO
        p.tiempo_inicio    = None
        p.tiempo_fin       = None
        p.tiempo_espera    = 0
        p.tiempo_ejecucion = 0
        p.tiempo_retorno   = 0

    pendientes = sorted(procesos, key=lambda p: p.tiempo_llegada)
    tiempo_actual = 0
    registro = []
    listos: List[Proceso] = []

    while pendientes or listos:
        # Agregar a listos los procesos que ya llegaron
        nuevos = [p for p in pendientes if p.tiempo_llegada <= tiempo_actual]
        for p in nuevos:
            p.estado = ESTADO_LISTO
            listos.append(p)
            pendientes.remove(p)

        if not listos:
            # CPU ociosa: avanzar al siguiente proceso pendiente
            tiempo_actual = pendientes[0].tiempo_llegada
            continue

        # Elegir el de mayor prioridad (menor número); desempate por llegada
        listos.sort(key=lambda p: (p.prioridad, p.tiempo_llegada))
        proceso = listos.pop(0)

        proceso.estado       = ESTADO_EJECUTANDO
        proceso.tiempo_inicio = tiempo_actual

        inicio_turno  = tiempo_actual
        tiempo_actual += proceso.duracion          # No expulsivo: corre hasta terminar
        proceso.tiempo_ejecucion = proceso.duracion
        proceso.tiempo_restante  = 0
        proceso.estado       = ESTADO_TERMINADO
        proceso.tiempo_fin   = tiempo_actual
        proceso.tiempo_retorno = proceso.tiempo_fin - proceso.tiempo_llegada
        proceso.tiempo_espera  = proceso.tiempo_retorno - proceso.duracion

        registro.append({
            "pid"          : proceso.pid,
            "nombre"       : proceso.nombre,
            "inicio"       : inicio_turno,
            "fin"          : tiempo_actual,
            "duracion_turno": proceso.duracion
        })

    return registro


# =============================================================================
# MÉTRICAS Y REPORTES
# =============================================================================

def calcular_metricas(procesos: List[Proceso]) -> dict:
    """
    Calcula las métricas globales del conjunto de procesos ya simulados.

    Retorna un diccionario con:
        - promedio_espera     : Tiempo promedio de espera.
        - promedio_ejecucion  : Tiempo promedio de ejecución (ráfaga real).
        - promedio_retorno    : Tiempo promedio de retorno (turnaround).
        - max_espera          : Máximo tiempo de espera observado.
        - min_espera          : Mínimo tiempo de espera observado.
        - throughput          : Procesos terminados / tiempo total de simulación.
    """
    terminados = [p for p in procesos if p.estado == ESTADO_TERMINADO]
    if not terminados:
        return {}

    esperas    = [p.tiempo_espera    for p in terminados]
    ejecuciones= [p.tiempo_ejecucion for p in terminados]
    retornos   = [p.tiempo_retorno   for p in terminados]

    tiempo_total = max(p.tiempo_fin for p in terminados)

    return {
        "promedio_espera"    : round(sum(esperas)     / len(terminados), 2),
        "promedio_ejecucion" : round(sum(ejecuciones) / len(terminados), 2),
        "promedio_retorno"   : round(sum(retornos)    / len(terminados), 2),
        "max_espera"         : max(esperas),
        "min_espera"         : min(esperas),
        "throughput"         : round(len(terminados) / tiempo_total, 4) if tiempo_total > 0 else 0,
    }


def imprimir_reporte(procesos: List[Proceso], algoritmo: str, metricas: dict) -> None:
    """
    Imprime en consola un reporte legible con los resultados de la simulación.

    Parámetros:
        procesos  : Lista de procesos simulados (con métricas ya calculadas).
        algoritmo : Nombre del algoritmo utilizado.
        metricas  : Diccionario devuelto por calcular_metricas().
    """
    ancho = 80
    sep   = "=" * ancho

    print(sep)
    print(f"  REPORTE DE PLANIFICACIÓN — Algoritmo: {algoritmo}")
    print(sep)

    # Encabezado de tabla
    print(f"{'PID':>4}  {'Nombre':<18}  {'Llegada':>7}  {'Duración':>8}  "
          f"{'Prioridad':>9}  {'Espera':>6}  {'Ejec.':>5}  {'Retorno':>7}  {'Estado':<10}")
    print("-" * ancho)

    for p in sorted(procesos, key=lambda x: x.pid):
        print(f"{p.pid:>4}  {p.nombre:<18}  {p.tiempo_llegada:>7}  {p.duracion:>8}  "
              f"{p.prioridad:>9}  {p.tiempo_espera:>6}  {p.tiempo_ejecucion:>5}  "
              f"{p.tiempo_retorno:>7}  {p.estado:<10}")

    print("-" * ancho)
    print("\n  MÉTRICAS GLOBALES")
    print(f"  {'Promedio de espera':<30}: {metricas.get('promedio_espera', 'N/A')}")
    print(f"  {'Promedio de ejecución':<30}: {metricas.get('promedio_ejecucion', 'N/A')}")
    print(f"  {'Promedio de retorno':<30}: {metricas.get('promedio_retorno', 'N/A')}")
    print(f"  {'Máx. tiempo de espera':<30}: {metricas.get('max_espera', 'N/A')}")
    print(f"  {'Mín. tiempo de espera':<30}: {metricas.get('min_espera', 'N/A')}")
    print(f"  {'Throughput (proc/unidad t.)':<30}: {metricas.get('throughput', 'N/A')}")
    print(sep)


def imprimir_diagrama_gantt(registro: List[dict], titulo: str = "") -> None:
    """
    Imprime un diagrama de Gantt simplificado en consola.

    Parámetros:
        registro : Lista devuelta por round_robin() o planificacion_prioridad().
        titulo   : Título opcional para el diagrama.
    """
    print(f"\n  DIAGRAMA DE GANTT — {titulo}")
    print("  " + "-" * 60)
    linea_superior = "  |"
    linea_inferior = "   "
    for entrada in registro:
        bloque = f" P{entrada['pid']}({entrada['duracion_turno']}) |"
        linea_superior += bloque
        marca_tiempo = str(entrada['inicio'])
        linea_inferior += marca_tiempo.ljust(len(bloque))
    print(linea_superior)
    linea_inferior += str(registro[-1]["fin"])
    print(linea_inferior)
    print("  " + "-" * 60 + "\n")


# =============================================================================
# BLOQUE DE PRUEBA / DEMO
# =============================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------ #
    #  Conjunto de procesos de ejemplo                                    #
    # ------------------------------------------------------------------ #
    procesos_ejemplo = [
        Proceso(pid=1, nombre="Navegador",    duracion=8,  prioridad=2, tiempo_llegada=0,  uso_cpu=45.0, acceso_archivos=False),
        Proceso(pid=2, nombre="Editor",       duracion=4,  prioridad=1, tiempo_llegada=1,  uso_cpu=20.0, acceso_archivos=True),
        Proceso(pid=3, nombre="Compilador",   duracion=9,  prioridad=3, tiempo_llegada=2,  uso_cpu=80.0, acceso_archivos=True),
        Proceso(pid=4, nombre="Reproductor",  duracion=5,  prioridad=2, tiempo_llegada=3,  uso_cpu=30.0, acceso_archivos=False),
        Proceso(pid=5, nombre="AntiVirus",    duracion=3,  prioridad=4, tiempo_llegada=4,  uso_cpu=60.0, acceso_archivos=True),
    ]

    # ------------------------------------------------------------------ #
    #  Simulación 1: Round Robin (quantum = 3)                            #
    # ------------------------------------------------------------------ #
    import copy
    procesos_rr = copy.deepcopy(procesos_ejemplo)

    print("\n>>> Ejecutando Round Robin con quantum = 3 ...\n")
    registro_rr = round_robin(procesos_rr, quantum=3)
    metricas_rr = calcular_metricas(procesos_rr)

    imprimir_diagrama_gantt(registro_rr, "Round Robin (quantum=3)")
    imprimir_reporte(procesos_rr, "Round Robin (quantum=3)", metricas_rr)

    # ------------------------------------------------------------------ #
    #  Simulación 2: Planificación por Prioridad                         #
    # ------------------------------------------------------------------ #
    procesos_prio = copy.deepcopy(procesos_ejemplo)

    print("\n>>> Ejecutando Planificación por Prioridad (no expulsiva) ...\n")
    registro_prio = planificacion_prioridad(procesos_prio)
    metricas_prio = calcular_metricas(procesos_prio)

    imprimir_diagrama_gantt(registro_prio, "Planificación por Prioridad")
    imprimir_reporte(procesos_prio, "Planificación por Prioridad", metricas_prio)

    # ------------------------------------------------------------------ #
    #  Comparativa rápida                                                 #
    # ------------------------------------------------------------------ #
    print("\n  COMPARATIVA DE ALGORITMOS")
    print(f"  {'Métrica':<35}  {'Round Robin':>12}  {'Prioridad':>10}")
    print("  " + "-" * 62)
    for clave in ["promedio_espera", "promedio_retorno", "throughput"]:
        print(f"  {clave:<35}  {metricas_rr.get(clave):>12}  {metricas_prio.get(clave):>10}")
    print()