"""
test_procesos.py - Casos de Prueba: Planificación de Procesos
==============================================================
Proyecto: Simulador de Sistema Operativo - 2026-1
Integrante 1: Planificación de Procesos
UPTC - Sistemas Operativos

Cómo ejecutar:
    python test_procesos.py
"""

import copy
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from procesos import (
    Proceso, ColaProcesos,
    round_robin, planificacion_prioridad,
    calcular_metricas,
    ESTADO_TERMINADO, ESTADO_LISTO, ESTADO_NUEVO
)

# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de prueba
# ─────────────────────────────────────────────────────────────────────────────

VERDE   = "\033[92m"
ROJO    = "\033[91m"
AMARILLO= "\033[93m"
AZUL    = "\033[94m"
CYAN    = "\033[96m"
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

_resultados = {"ok": 0, "fallo": 0}

def afirmar(condicion: bool, descripcion: str, detalle: str = "") -> None:
    if condicion:
        print(f"    {VERDE}✔{RESET}  {descripcion}")
        _resultados["ok"] += 1
    else:
        print(f"    {ROJO}✘{RESET}  {BOLD}{descripcion}{RESET}")
        if detalle:
            print(f"       {AMARILLO}↳ {detalle}{RESET}")
        _resultados["fallo"] += 1

def titulo(codigo: str, texto: str) -> None:
    print(f"\n  {CYAN}{BOLD}{codigo}{RESET}  {BOLD}{texto}{RESET}")
    print(f"  {DIM}{'─' * 55}{RESET}")

def seccion(texto: str) -> None:
    print(f"\n{BOLD}{'━' * 60}{RESET}")
    print(f"{BOLD}  {texto}{RESET}")
    print(f"{BOLD}{'━' * 60}{RESET}")

def resumen() -> None:
    total  = _resultados["ok"] + _resultados["fallo"]
    fallos = _resultados["fallo"]
    print(f"\n{'━' * 60}")
    barra_ok   = "█" * _resultados["ok"]
    barra_fail = "░" * fallos
    color_barra = VERDE if fallos == 0 else ROJO
    print(f"  {color_barra}{barra_ok}{barra_fail}{RESET}  {_resultados['ok']}/{total} pruebas")
    print()
    if fallos == 0:
        print(f"  {VERDE}{BOLD}✔  Todas las pruebas pasaron correctamente.{RESET}")
    else:
        print(f"  {ROJO}{BOLD}✘  {fallos} prueba(s) fallaron.{RESET}")
    print(f"{'━' * 60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 1 — Estructura de datos
# ─────────────────────────────────────────────────────────────────────────────

def test_estructura_proceso():
    titulo("CP-01", "Estructura de datos: clase Proceso")

    p = Proceso(pid=7, nombre="Navegador", duracion=8, prioridad=2,
                tiempo_llegada=3, uso_cpu=45.0, acceso_archivos=True)

    afirmar(p.pid == 7,                  "PID asignado correctamente")
    afirmar(p.nombre == "Navegador",     "Nombre asignado correctamente")
    afirmar(p.duracion == 8,             "Duración asignada correctamente")
    afirmar(p.prioridad == 2,            "Prioridad asignada correctamente")
    afirmar(p.tiempo_llegada == 3,       "Tiempo de llegada asignado correctamente")
    afirmar(p.uso_cpu == 45.0,           "Uso de CPU asignado correctamente")
    afirmar(p.acceso_archivos == True,   "Acceso a archivos asignado correctamente")
    afirmar(p.estado == ESTADO_NUEVO,    "Estado inicial = NUEVO")
    afirmar(p.tiempo_restante == 8,      "tiempo_restante inicializado igual a duración")
    afirmar(p.tiempo_inicio is None,     "tiempo_inicio inicial = None")
    afirmar(p.tiempo_fin is None,        "tiempo_fin inicial = None")
    afirmar(p.tiempo_espera == 0,        "tiempo_espera inicial = 0")
    afirmar(p.tiempo_ejecucion == 0,     "tiempo_ejecucion inicial = 0")
    afirmar(p.tiempo_retorno == 0,       "tiempo_retorno inicial = 0")


def test_proceso_valores_default():
    titulo("CP-02", "Proceso: valores por defecto")

    p = Proceso(pid=1, nombre="Test", duracion=3)

    afirmar(p.prioridad == 0,            "Prioridad por defecto = 0")
    afirmar(p.tiempo_llegada == 0,       "tiempo_llegada por defecto = 0")
    afirmar(p.uso_cpu == 0.0,            "uso_cpu por defecto = 0.0")
    afirmar(p.acceso_archivos == False,  "acceso_archivos por defecto = False")
    afirmar(p.tiempo_restante == 3,      "tiempo_restante = duración al crear")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 2 — Cola de Procesos
# ─────────────────────────────────────────────────────────────────────────────

def test_cola_vacia():
    titulo("CP-03", "ColaProcesos: estado inicial vacío")

    cola = ColaProcesos()
    afirmar(cola.esta_vacia(),       "Cola recién creada está vacía")
    afirmar(cola.tamanio() == 0,     "Tamaño inicial = 0")
    afirmar(cola.quitar_frente() is None, "quitar_frente() en vacía devuelve None")
    afirmar(cola.ver_cola() == [],   "ver_cola() en vacía devuelve lista vacía")


def test_cola_agregar():
    titulo("CP-04", "ColaProcesos: agregar procesos")

    cola = ColaProcesos()
    p1 = Proceso(pid=1, nombre="A", duracion=3)
    p2 = Proceso(pid=2, nombre="B", duracion=5)

    cola.agregar(p1)
    afirmar(p1.estado == ESTADO_LISTO,  "Proceso marcado LISTO al agregar")
    afirmar(not cola.esta_vacia(),      "Cola no vacía tras agregar")
    afirmar(cola.tamanio() == 1,        "Tamaño = 1 tras agregar p1")

    cola.agregar(p2)
    afirmar(cola.tamanio() == 2,        "Tamaño = 2 tras agregar p2")


def test_cola_fifo():
    titulo("CP-05", "ColaProcesos: orden FIFO al extraer")

    cola = ColaProcesos()
    pids = [1, 2, 3, 4]
    for pid in pids:
        cola.agregar(Proceso(pid=pid, nombre=f"P{pid}", duracion=2))

    for esperado in pids:
        extraido = cola.quitar_frente()
        afirmar(extraido.pid == esperado,
                f"Extraído P{extraido.pid}, esperado P{esperado}")

    afirmar(cola.esta_vacia(), "Cola vacía tras extraer todos los procesos")


def test_cola_ver_no_modifica():
    titulo("CP-06", "ColaProcesos: ver_cola() no modifica la cola")

    cola = ColaProcesos()
    cola.agregar(Proceso(pid=1, nombre="X", duracion=2))
    cola.agregar(Proceso(pid=2, nombre="Y", duracion=4))

    vista = cola.ver_cola()
    afirmar(len(vista) == 2,        "ver_cola() devuelve 2 elementos")
    afirmar(cola.tamanio() == 2,    "Tamaño no cambió tras ver_cola()")
    afirmar(vista[0].pid == 1,      "Primer elemento es P1")
    afirmar(vista[1].pid == 2,      "Segundo elemento es P2")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 3 — Round Robin
# ─────────────────────────────────────────────────────────────────────────────

def test_rr_proceso_unico():
    titulo("CP-07", "Round Robin: proceso único")

    p = Proceso(pid=1, nombre="Solo", duracion=4, tiempo_llegada=0)
    registro = round_robin([p], quantum=3)

    afirmar(p.estado == ESTADO_TERMINADO, "Estado = TERMINADO")
    afirmar(p.tiempo_ejecucion == 4,      "tiempo_ejecucion = duración total (4)")
    afirmar(p.tiempo_espera == 0,         "tiempo_espera = 0 (único proceso)")
    afirmar(p.tiempo_retorno == 4,        "tiempo_retorno = 4 - 0 = 4")
    afirmar(p.tiempo_restante == 0,       "tiempo_restante = 0 al terminar")
    afirmar(len(registro) == 2,           "Registro: 2 turnos (quantum=3 + resto=1)")


def test_rr_quantum_mayor_duracion():
    titulo("CP-08", "Round Robin: quantum mayor que duración del proceso")

    p = Proceso(pid=1, nombre="Corto", duracion=2, tiempo_llegada=0)
    registro = round_robin([p], quantum=10)

    afirmar(p.estado == ESTADO_TERMINADO, "Proceso termina correctamente")
    afirmar(p.tiempo_ejecucion == 2,      "Ejecuta solo su duración real (2), no el quantum (10)")
    afirmar(len(registro) == 1,           "Un solo turno en el registro")


def test_rr_misma_llegada():
    titulo("CP-09", "Round Robin: múltiples procesos con llegada simultánea")

    procesos = [
        Proceso(pid=1, nombre="P1", duracion=4, tiempo_llegada=0),
        Proceso(pid=2, nombre="P2", duracion=3, tiempo_llegada=0),
        Proceso(pid=3, nombre="P3", duracion=5, tiempo_llegada=0),
    ]
    round_robin(procesos, quantum=2)

    for p in procesos:
        afirmar(p.estado == ESTADO_TERMINADO,
                f"P{p.pid} termina con estado TERMINADO")
        afirmar(p.tiempo_ejecucion == p.duracion,
                f"P{p.pid} ejecutó exactamente su duración ({p.duracion})",
                f"tiempo_ejecucion={p.tiempo_ejecucion}")
        afirmar(p.tiempo_espera >= 0,
                f"P{p.pid} tiene tiempo de espera no negativo",
                f"tiempo_espera={p.tiempo_espera}")
        afirmar(p.tiempo_retorno == p.tiempo_espera + p.duracion,
                f"P{p.pid}: retorno = espera + duración",
                f"retorno={p.tiempo_retorno}, espera+dur={p.tiempo_espera+p.duracion}")


def test_rr_llegadas_escalonadas():
    titulo("CP-10", "Round Robin: procesos con llegadas escalonadas")

    procesos = [
        Proceso(pid=1, nombre="P1", duracion=6, tiempo_llegada=0),
        Proceso(pid=2, nombre="P2", duracion=4, tiempo_llegada=3),
        Proceso(pid=3, nombre="P3", duracion=2, tiempo_llegada=7),
    ]
    registro = round_robin(procesos, quantum=3)

    for p in procesos:
        afirmar(p.estado == ESTADO_TERMINADO,
                f"P{p.pid} termina correctamente")
        afirmar(p.tiempo_fin >= p.tiempo_llegada + p.duracion,
                f"P{p.pid}: tiempo_fin >= llegada + duración",
                f"fin={p.tiempo_fin}, llegada+dur={p.tiempo_llegada+p.duracion}")

    # El registro debe estar en orden cronológico (sin huecos)
    for i in range(1, len(registro)):
        afirmar(registro[i]["inicio"] == registro[i-1]["fin"],
                f"Turno {i}: inicio contiguo al fin anterior (sin huecos de CPU)",
                f"inicio={registro[i]['inicio']}, fin_anterior={registro[i-1]['fin']}")


def test_rr_idempotencia():
    titulo("CP-11", "Round Robin: re-ejecutar sobre el mismo lote da mismos resultados")

    procesos = [
        Proceso(pid=1, nombre="P1", duracion=5, tiempo_llegada=0),
        Proceso(pid=2, nombre="P2", duracion=3, tiempo_llegada=1),
    ]

    round_robin(procesos, quantum=2)
    esperas_1 = {p.pid: p.tiempo_espera for p in procesos}

    round_robin(procesos, quantum=2)
    esperas_2 = {p.pid: p.tiempo_espera for p in procesos}

    for pid in esperas_1:
        afirmar(esperas_1[pid] == esperas_2[pid],
                f"P{pid}: misma espera en ambas ejecuciones ({esperas_1[pid]})")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 4 — Planificación por Prioridad
# ─────────────────────────────────────────────────────────────────────────────

def test_prioridad_orden_ejecucion():
    titulo("CP-12", "Prioridad: orden correcto de ejecución (no expulsivo)")

    procesos = [
        Proceso(pid=1, nombre="BajaPrio",  duracion=3, prioridad=5, tiempo_llegada=0),
        Proceso(pid=2, nombre="AltaPrio",  duracion=2, prioridad=1, tiempo_llegada=0),
        Proceso(pid=3, nombre="MediaPrio", duracion=4, prioridad=3, tiempo_llegada=0),
    ]
    registro = planificacion_prioridad(procesos)
    pids = [e["pid"] for e in registro]

    # Todos llegan en t=0 → se ordena por prioridad directamente
    # P2(prio=1) > P3(prio=3) > P1(prio=5)
    afirmar(pids[0] == 2, "P2 ejecuta primero (prioridad=1, la más alta)")
    afirmar(pids[1] == 3, "P3 ejecuta segundo (prioridad=3)")
    afirmar(pids[2] == 1, "P1 ejecuta tercero (prioridad=5, la más baja)")

    for p in procesos:
        afirmar(p.estado == ESTADO_TERMINADO, f"P{p.pid} termina correctamente")


def test_prioridad_no_expulsivo():
    titulo("CP-13", "Prioridad: proceso de alta prioridad que llega tarde NO expulsa")

    procesos = [
        Proceso(pid=1, nombre="Largo",   duracion=10, prioridad=3, tiempo_llegada=0),
        Proceso(pid=2, nombre="Urgente", duracion=2,  prioridad=1, tiempo_llegada=5),
    ]
    registro = planificacion_prioridad(procesos)
    pids = [e["pid"] for e in registro]

    afirmar(pids[0] == 1,
            "P1 no es expulsado aunque P2 llegue con mayor prioridad (no expulsivo)")
    afirmar(pids[1] == 2,
            "P2 ejecuta segundo, tras terminar P1")

    p2 = next(p for p in procesos if p.pid == 2)
    afirmar(p2.tiempo_espera == 5,
            f"Espera de P2 = 5 (CPU libre en t=10, llegó en t=5)",
            f"tiempo_espera={p2.tiempo_espera}")


def test_prioridad_desempate_llegada():
    titulo("CP-14", "Prioridad: desempate por tiempo de llegada (FCFS)")

    procesos = [
        Proceso(pid=1, nombre="Primero",     duracion=1, prioridad=1, tiempo_llegada=0),
        Proceso(pid=2, nombre="IgualPrio_A", duracion=3, prioridad=2, tiempo_llegada=1),
        Proceso(pid=3, nombre="IgualPrio_B", duracion=3, prioridad=2, tiempo_llegada=2),
    ]
    registro = planificacion_prioridad(procesos)
    pids = [e["pid"] for e in registro]

    afirmar(pids[0] == 1, "P1 primero (prioridad=1, llega en t=0)")
    afirmar(pids[1] == 2, "P2 segundo (igual prioridad que P3, pero llegó antes)")
    afirmar(pids[2] == 3, "P3 tercero (llegó después que P2)")


def test_prioridad_un_turno_por_proceso():
    titulo("CP-15", "Prioridad: cada proceso ocupa exactamente un turno (no expulsivo)")

    procesos = [
        Proceso(pid=i, nombre=f"P{i}", duracion=i+1, prioridad=i, tiempo_llegada=0)
        for i in range(1, 5)
    ]
    registro = planificacion_prioridad(procesos)

    for pid in range(1, 5):
        turnos = [e for e in registro if e["pid"] == pid]
        afirmar(len(turnos) == 1,
                f"P{pid} aparece exactamente una vez en el registro (no expulsivo)",
                f"Aparece {len(turnos)} vez/veces")


def test_prioridad_idempotencia():
    titulo("CP-16", "Prioridad: re-ejecutar sobre el mismo lote da mismos resultados")

    procesos = [
        Proceso(pid=1, nombre="P1", duracion=5, prioridad=2, tiempo_llegada=0),
        Proceso(pid=2, nombre="P2", duracion=3, prioridad=1, tiempo_llegada=1),
    ]

    planificacion_prioridad(procesos)
    esperas_1 = {p.pid: p.tiempo_espera for p in procesos}

    planificacion_prioridad(procesos)
    esperas_2 = {p.pid: p.tiempo_espera for p in procesos}

    for pid in esperas_1:
        afirmar(esperas_1[pid] == esperas_2[pid],
                f"P{pid}: misma espera en ambas ejecuciones ({esperas_1[pid]})")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 5 — Métricas
# ─────────────────────────────────────────────────────────────────────────────

def test_metricas_claves_presentes():
    titulo("CP-17", "Métricas: todas las claves están presentes")

    procesos = [
        Proceso(pid=1, nombre="M1", duracion=4, tiempo_llegada=0),
        Proceso(pid=2, nombre="M2", duracion=6, tiempo_llegada=0),
    ]
    round_robin(procesos, quantum=100)
    m = calcular_metricas(procesos)

    for clave in ["promedio_espera", "promedio_ejecucion", "promedio_retorno",
                  "max_espera", "min_espera", "throughput"]:
        afirmar(clave in m, f"Clave '{clave}' presente en el diccionario de métricas")


def test_metricas_valores_rr_demo():
    titulo("CP-18", "Métricas: valores exactos con lote demo — Round Robin (q=3)")

    procesos = [
        Proceso(pid=1, nombre="Navegador",   duracion=8,  prioridad=2, tiempo_llegada=0),
        Proceso(pid=2, nombre="Editor",      duracion=4,  prioridad=1, tiempo_llegada=1),
        Proceso(pid=3, nombre="Compilador",  duracion=9,  prioridad=3, tiempo_llegada=2),
        Proceso(pid=4, nombre="Reproductor", duracion=5,  prioridad=2, tiempo_llegada=3),
        Proceso(pid=5, nombre="AntiVirus",   duracion=3,  prioridad=4, tiempo_llegada=4),
    ]
    round_robin(procesos, quantum=3)
    m = calcular_metricas(procesos)

    afirmar(m["promedio_espera"]  == 15.4,   f"Promedio espera = 15.4",  f"obtenido: {m['promedio_espera']}")
    afirmar(m["promedio_retorno"] == 21.2,   f"Promedio retorno = 21.2", f"obtenido: {m['promedio_retorno']}")
    afirmar(m["throughput"]       == 0.1724, f"Throughput = 0.1724",     f"obtenido: {m['throughput']}")


def test_metricas_valores_prioridad_demo():
    titulo("CP-19", "Métricas: valores exactos con lote demo — Prioridad")

    procesos = [
        Proceso(pid=1, nombre="Navegador",   duracion=8,  prioridad=2, tiempo_llegada=0),
        Proceso(pid=2, nombre="Editor",      duracion=4,  prioridad=1, tiempo_llegada=1),
        Proceso(pid=3, nombre="Compilador",  duracion=9,  prioridad=3, tiempo_llegada=2),
        Proceso(pid=4, nombre="Reproductor", duracion=5,  prioridad=2, tiempo_llegada=3),
        Proceso(pid=5, nombre="AntiVirus",   duracion=3,  prioridad=4, tiempo_llegada=4),
    ]
    planificacion_prioridad(procesos)
    m = calcular_metricas(procesos)

    afirmar(m["promedio_espera"]  == 10.6,   f"Promedio espera = 10.6",  f"obtenido: {m['promedio_espera']}")
    afirmar(m["promedio_retorno"] == 16.4,   f"Promedio retorno = 16.4", f"obtenido: {m['promedio_retorno']}")
    afirmar(m["throughput"]       == 0.1724, f"Throughput = 0.1724",     f"obtenido: {m['throughput']}")


def test_metricas_invariantes():
    titulo("CP-20", "Métricas: invariantes matemáticas siempre se cumplen")

    for quantum in [1, 2, 5]:
        procesos = [
            Proceso(pid=i, nombre=f"P{i}", duracion=i+1, prioridad=i,
                    tiempo_llegada=i) for i in range(1, 6)
        ]
        round_robin(procesos, quantum=quantum)
        m = calcular_metricas(procesos)

        afirmar(m["max_espera"] >= m["min_espera"],
                f"[q={quantum}] max_espera >= min_espera")
        afirmar(m["min_espera"] <= m["promedio_espera"] <= m["max_espera"],
                f"[q={quantum}] min <= promedio <= max")
        afirmar(m["throughput"] > 0,
                f"[q={quantum}] throughput > 0")


def test_metricas_lista_vacia():
    titulo("CP-21", "Métricas: lista vacía devuelve dict vacío sin error")

    m = calcular_metricas([])
    afirmar(m == {}, "calcular_metricas([]) = {}")

    procesos = [Proceso(pid=1, nombre="X", duracion=3)]
    # Sin ejecutar ningún algoritmo — nadie está TERMINADO
    m2 = calcular_metricas(procesos)
    afirmar(m2 == {}, "calcular_metricas() sin procesos terminados = {}")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 6 — Consistencia general
# ─────────────────────────────────────────────────────────────────────────────

def test_consistencia_retorno():
    titulo("CP-22", "Consistencia: tiempo_retorno = espera + ejecución (ambos algoritmos)")

    base = [
        Proceso(pid=i, nombre=f"P{i}", duracion=i+2, prioridad=i,
                tiempo_llegada=i) for i in range(1, 6)
    ]

    for nombre_alg, func, kwargs in [
        ("Round Robin", round_robin,            {"quantum": 2}),
        ("Prioridad",   planificacion_prioridad, {}),
    ]:
        copia = copy.deepcopy(base)
        func(copia, **kwargs)
        for p in copia:
            afirmar(
                p.tiempo_retorno == p.tiempo_espera + p.tiempo_ejecucion,
                f"[{nombre_alg}] P{p.pid}: retorno({p.tiempo_retorno}) = "
                f"espera({p.tiempo_espera}) + ejec({p.tiempo_ejecucion})"
            )


def test_consistencia_tiempo_restante():
    titulo("CP-23", "Consistencia: tiempo_restante = 0 al terminar (ambos algoritmos)")

    base = [
        Proceso(pid=i, nombre=f"P{i}", duracion=i+1, prioridad=i,
                tiempo_llegada=0) for i in range(1, 5)
    ]

    for nombre_alg, func, kwargs in [
        ("Round Robin", round_robin,            {"quantum": 3}),
        ("Prioridad",   planificacion_prioridad, {}),
    ]:
        copia = copy.deepcopy(base)
        func(copia, **kwargs)
        for p in copia:
            afirmar(p.tiempo_restante == 0,
                    f"[{nombre_alg}] P{p.pid}: tiempo_restante = 0 al terminar",
                    f"tiempo_restante={p.tiempo_restante}")


def test_consistencia_ejecucion_igual_duracion():
    titulo("CP-24", "Consistencia: tiempo_ejecucion = duración original (ambos algoritmos)")

    base = [
        Proceso(pid=i, nombre=f"P{i}", duracion=i*2+1, prioridad=i,
                tiempo_llegada=i) for i in range(1, 5)
    ]

    for nombre_alg, func, kwargs in [
        ("Round Robin", round_robin,            {"quantum": 2}),
        ("Prioridad",   planificacion_prioridad, {}),
    ]:
        duraciones = {p.pid: p.duracion for p in base}
        copia = copy.deepcopy(base)
        func(copia, **kwargs)
        for p in copia:
            afirmar(p.tiempo_ejecucion == duraciones[p.pid],
                    f"[{nombre_alg}] P{p.pid}: tiempo_ejecucion({p.tiempo_ejecucion}) = duración({duraciones[p.pid]})")


def test_espera_no_negativa_ambos():
    titulo("CP-25", "Consistencia: tiempo_espera >= 0 siempre (ambos algoritmos)")

    base = [
        Proceso(pid=i, nombre=f"P{i}", duracion=i+2, prioridad=(5-i),
                tiempo_llegada=i*2) for i in range(1, 6)
    ]

    for nombre_alg, func, kwargs in [
        ("Round Robin", round_robin,            {"quantum": 3}),
        ("Prioridad",   planificacion_prioridad, {}),
    ]:
        copia = copy.deepcopy(base)
        func(copia, **kwargs)
        for p in copia:
            afirmar(p.tiempo_espera >= 0,
                    f"[{nombre_alg}] P{p.pid}: tiempo_espera >= 0",
                    f"tiempo_espera={p.tiempo_espera}")


# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{BOLD}{'━' * 60}")
    print("  SUITE DE PRUEBAS — procesos.py")
    print("  Simulador SO 2026-1  |  Integrante 1: Planificación")
    print(f"{'━' * 60}{RESET}")

    seccion("BLOQUE 1 — Estructura de datos")
    test_estructura_proceso()
    test_proceso_valores_default()

    seccion("BLOQUE 2 — Cola de Procesos")
    test_cola_vacia()
    test_cola_agregar()
    test_cola_fifo()
    test_cola_ver_no_modifica()

    seccion("BLOQUE 3 — Round Robin")
    test_rr_proceso_unico()
    test_rr_quantum_mayor_duracion()
    test_rr_misma_llegada()
    test_rr_llegadas_escalonadas()
    test_rr_idempotencia()

    seccion("BLOQUE 4 — Planificación por Prioridad")
    test_prioridad_orden_ejecucion()
    test_prioridad_no_expulsivo()
    test_prioridad_desempate_llegada()
    test_prioridad_un_turno_por_proceso()
    test_prioridad_idempotencia()

    seccion("BLOQUE 5 — Métricas")
    test_metricas_claves_presentes()
    test_metricas_valores_rr_demo()
    test_metricas_valores_prioridad_demo()
    test_metricas_invariantes()
    test_metricas_lista_vacia()

    seccion("BLOQUE 6 — Consistencia general")
    test_consistencia_retorno()
    test_consistencia_tiempo_restante()
    test_consistencia_ejecucion_igual_duracion()
    test_espera_no_negativa_ambos()

    resumen()