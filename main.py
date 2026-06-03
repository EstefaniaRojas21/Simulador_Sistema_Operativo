from procesos import (
    Proceso,
    round_robin,
    planificacion_prioridad,
    calcular_metricas,
    imprimir_reporte,
    imprimir_diagrama_gantt
)

import copy


def main():

    procesos_ejemplo = [
        Proceso(pid=1, nombre="Navegador",   duracion=8, prioridad=2, tiempo_llegada=0),
        Proceso(pid=2, nombre="Editor",      duracion=4, prioridad=1, tiempo_llegada=1),
        Proceso(pid=3, nombre="Compilador",  duracion=9, prioridad=3, tiempo_llegada=2),
        Proceso(pid=4, nombre="Reproductor", duracion=5, prioridad=2, tiempo_llegada=3),
        Proceso(pid=5, nombre="Antivirus",   duracion=3, prioridad=4, tiempo_llegada=4)
    ]

    print("\n===== ROUND ROBIN =====")

    procesos_rr = copy.deepcopy(procesos_ejemplo)

    registro_rr = round_robin(procesos_rr, quantum=3)
    metricas_rr = calcular_metricas(procesos_rr)

    imprimir_diagrama_gantt(registro_rr, "Round Robin")
    imprimir_reporte(
        procesos_rr,
        "Round Robin",
        metricas_rr
    )

    print("\n===== PRIORIDAD =====")

    procesos_prio = copy.deepcopy(procesos_ejemplo)

    registro_prio = planificacion_prioridad(procesos_prio)
    metricas_prio = calcular_metricas(procesos_prio)

    imprimir_diagrama_gantt(registro_prio, "Prioridad")
    imprimir_reporte(
        procesos_prio,
        "Prioridad",
        metricas_prio
    )


if __name__ == "__main__":
    main()