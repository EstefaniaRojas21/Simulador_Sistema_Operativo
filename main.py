import copy
from procesos import (
    Proceso,
    round_robin,
    planificacion_prioridad,
    simular_sistema_completo,
    calcular_metricas,
    imprimir_reporte,
    imprimir_diagrama_gantt
)

def ejecutar_simulacion_simple(procesos_ejemplo):
    print("\n" + "=" * 80)
    print(" 1. SIMULACIÓN SIMPLE DE CPU (SIN MEMORIA NI ARCHIVOS)")
    print("=" * 80)

    print("\n===== ROUND ROBIN =====")
    procesos_rr = copy.deepcopy(procesos_ejemplo)
    registro_rr = round_robin(procesos_rr, quantum=3)
    metricas_rr = calcular_metricas(procesos_rr)
    imprimir_diagrama_gantt(registro_rr, "Round Robin")
    imprimir_reporte(procesos_rr, "Round Robin", metricas_rr)

    print("\n===== PRIORIDAD =====")
    procesos_prio = copy.deepcopy(procesos_ejemplo)
    registro_prio = planificacion_prioridad(procesos_prio)
    metricas_prio = calcular_metricas(procesos_prio)
    imprimir_diagrama_gantt(registro_prio, "Prioridad")
    imprimir_reporte(procesos_prio, "Prioridad", metricas_prio)


def ejecutar_simulacion_integrada(procesos_ejemplo):
    print("\n" + "=" * 80)
    print(" 2. SIMULACIÓN INTEGRADA (PLANIFICACIÓN + MEMORIA + ARCHIVOS CON CONCURRENCIA)")
    print("=" * 80)

    # Definir una secuencia de accesos a páginas y archivos para que sea interesante
    # Procesos con accesos específicos a páginas y archivos
    procesos_complejos = [
        Proceso(pid=1, nombre="Navegador", duracion=8, prioridad=2, tiempo_llegada=0,
                uso_cpu=45.0, acceso_archivos=True,
                secuencia_paginas=[0, 1, 2, 0, 3, 0, 4, 2], archivos_requeridos=["datos.txt"]),
        
        Proceso(pid=2, nombre="Editor", duracion=4, prioridad=1, tiempo_llegada=1,
                uso_cpu=20.0, acceso_archivos=True,
                secuencia_paginas=[1, 2, 1, 2], archivos_requeridos=["datos.txt", "config.json"]),
        
        Proceso(pid=3, nombre="Compilador", duracion=9, prioridad=3, tiempo_llegada=2,
                uso_cpu=80.0, acceso_archivos=False,
                secuencia_paginas=[0, 3, 4, 0, 1, 2, 3, 4, 0]),
        
        Proceso(pid=4, nombre="Reproductor", duracion=5, prioridad=2, tiempo_llegada=3,
                uso_cpu=30.0, acceso_archivos=True,
                secuencia_paginas=[2, 3, 2, 3, 0], archivos_requeridos=["config.json"]),
        
        Proceso(pid=5, nombre="Antivirus", duracion=3, prioridad=4, tiempo_llegada=4,
                uso_cpu=60.0, acceso_archivos=True,
                secuencia_paginas=[0, 1, 2], archivos_requeridos=["log.db"])
    ]

    # Ejecutar simulación con Round Robin y reemplazo FIFO
    print("\n>>> Ejecutando Simulación Integrada: Planificación RR (q=3) + Memoria FIFO (4 marcos) ...\n")
    proc_sim = copy.deepcopy(procesos_complejos)
    res_fifo = simular_sistema_completo(
        procesos=proc_sim,
        algoritmo_planif="RR",
        quantum=3,
        algoritmo_memoria="FIFO",
        num_marcos_memoria=4,
        lista_archivos=["datos.txt", "config.json", "log.db"]
    )

    imprimir_trazado_pasos(res_fifo["historial"])
    imprimir_diagrama_gantt(res_fifo["registro"], "Simulación Integrada (Planif: RR, Memoria: FIFO)")
    metricas_fifo = calcular_metricas(proc_sim)
    imprimir_reporte(proc_sim, "Integrado RR + Memoria FIFO", metricas_fifo)
    print(f"Total Fallos de Página (FIFO): {res_fifo['fallos_memoria']}")

    print("\n--- Bitácora de Gestión de Archivos (Mutex y Conflictos) ---")
    for log in res_fifo["bitacora_archivos"]:
        print(f"  {log}")

    # Ejecutar simulación con Round Robin y reemplazo LRU
    print("\n\n>>> Ejecutando Simulación Integrada: Planificación RR (q=3) + Memoria LRU (4 marcos) ...\n")
    proc_sim_lru = copy.deepcopy(procesos_complejos)
    res_lru = simular_sistema_completo(
        procesos=proc_sim_lru,
        algoritmo_planif="RR",
        quantum=3,
        algoritmo_memoria="LRU",
        num_marcos_memoria=4,
        lista_archivos=["datos.txt", "config.json", "log.db"]
    )
    metricas_lru = calcular_metricas(proc_sim_lru)
    print(f"Total Fallos de Página (LRU): {res_lru['fallos_memoria']}")
    
    # Comparativa de reemplazo
    print("\n" + "-" * 50)
    print(" COMPARATIVA DE ALGORITMOS DE REEMPLAZO DE PÁGINAS")
    print("-" * 50)
    print(f"  Fallos de Página con FIFO : {res_fifo['fallos_memoria']}")
    print(f"  Fallos de Página con LRU  : {res_lru['fallos_memoria']}")
    print("-" * 50 + "\n")


def imprimir_trazado_pasos(historial):
    print(f"{'Tiempo':<8} | {'CPU Running':<18} | {'Pág. Req':<8} | {'Res Memoria':<32} | {'Marcos Física':<35}")
    print("-" * 115)
    for paso in historial:
        cpu = paso.get("cpu", "-")
        pag = paso.get("pagina_solicitada", "-")
        res_mem = paso.get("resultado_memoria", "-")
        mem_vis = paso.get("memoria", "[]")
        print(f"{paso['tiempo']:<8} | {cpu:<18} | {str(pag):<8} | {res_mem:<32} | {mem_vis:<35}")
    print("-" * 115)


def main():
    procesos_ejemplo = [
        Proceso(pid=1, nombre="Navegador",   duracion=8, prioridad=2, tiempo_llegada=0),
        Proceso(pid=2, nombre="Editor",      duracion=4, prioridad=1, tiempo_llegada=1),
        Proceso(pid=3, nombre="Compilador",  duracion=9, prioridad=3, tiempo_llegada=2),
        Proceso(pid=4, nombre="Reproductor", duracion=5, prioridad=2, tiempo_llegada=3),
        Proceso(pid=5, nombre="Antivirus",   duracion=3, prioridad=4, tiempo_llegada=4)
    ]

    ejecutar_simulacion_simple(procesos_ejemplo)
    ejecutar_simulacion_integrada(procesos_ejemplo)


if __name__ == "__main__":
    main()