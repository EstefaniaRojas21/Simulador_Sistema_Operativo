"""
server.py - HTTP Server for OS Simulator Frontend
===================================================
Serves the web frontend and provides API endpoints
for running simulations and returning results as JSON.

Usage:
    python server.py
    Open http://localhost:8080 in your browser
"""

import http.server
import json
import os
import sys
from urllib.parse import urlparse

# Ensure project root is in path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from procesos import (
    Proceso, round_robin, planificacion_prioridad,
    simular_sistema_completo, calcular_metricas
)

PORT = 8080
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')


def crear_procesos_ejemplo():
    """Create sample processes for simple CPU simulation."""
    return [
        Proceso(pid=1, nombre="Navegador",   duracion=8,  prioridad=2, tiempo_llegada=0),
        Proceso(pid=2, nombre="Editor",      duracion=4,  prioridad=1, tiempo_llegada=1),
        Proceso(pid=3, nombre="Compilador",  duracion=9,  prioridad=3, tiempo_llegada=2),
        Proceso(pid=4, nombre="Reproductor", duracion=5,  prioridad=2, tiempo_llegada=3),
        Proceso(pid=5, nombre="Antivirus",   duracion=3,  prioridad=4, tiempo_llegada=4),
    ]


def crear_procesos_integrados():
    """Create processes with memory and file access for integrated simulation."""
    return [
        Proceso(pid=1, nombre="Navegador", duracion=8, prioridad=2, tiempo_llegada=0,
                uso_cpu=45.0, acceso_archivos=True,
                secuencia_paginas=[0, 1, 2, 0, 3, 0, 4, 2],
                archivos_requeridos=["datos.txt"]),
        Proceso(pid=2, nombre="Editor", duracion=4, prioridad=1, tiempo_llegada=1,
                uso_cpu=20.0, acceso_archivos=True,
                secuencia_paginas=[1, 2, 1, 2],
                archivos_requeridos=["datos.txt", "config.json"]),
        Proceso(pid=3, nombre="Compilador", duracion=9, prioridad=3, tiempo_llegada=2,
                uso_cpu=80.0, acceso_archivos=False,
                secuencia_paginas=[0, 3, 4, 0, 1, 2, 3, 4, 0]),
        Proceso(pid=4, nombre="Reproductor", duracion=5, prioridad=2, tiempo_llegada=3,
                uso_cpu=30.0, acceso_archivos=True,
                secuencia_paginas=[2, 3, 2, 3, 0],
                archivos_requeridos=["config.json"]),
        Proceso(pid=5, nombre="Antivirus", duracion=3, prioridad=4, tiempo_llegada=4,
                uso_cpu=60.0, acceso_archivos=True,
                secuencia_paginas=[0, 1, 2],
                archivos_requeridos=["log.db"])
    ]


def proceso_a_dict(p):
    """Convert a Proceso dataclass instance to a JSON-serializable dict."""
    return {
        "pid": p.pid,
        "nombre": p.nombre,
        "duracion": p.duracion,
        "prioridad": p.prioridad,
        "tiempo_llegada": p.tiempo_llegada,
        "uso_cpu": p.uso_cpu,
        "acceso_archivos": p.acceso_archivos,
        "estado": p.estado,
        "tiempo_restante": p.tiempo_restante,
        "tiempo_inicio": p.tiempo_inicio,
        "tiempo_fin": p.tiempo_fin,
        "tiempo_espera": p.tiempo_espera,
        "tiempo_ejecucion": p.tiempo_ejecucion,
        "tiempo_retorno": p.tiempo_retorno,
    }


class SimuladorHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the simulator frontend and API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/simulacion-simple':
            self._handle_simulacion_simple()
        elif parsed.path == '/api/simulacion-integrada':
            self._handle_simulacion_integrada()
        else:
            super().do_GET()

    def _handle_simulacion_simple(self):
        """Run Round Robin and Priority simulations, return JSON."""
        procesos_rr = crear_procesos_ejemplo()
        registro_rr = round_robin(procesos_rr, quantum=3)
        metricas_rr = calcular_metricas(procesos_rr)

        procesos_prio = crear_procesos_ejemplo()
        registro_prio = planificacion_prioridad(procesos_prio)
        metricas_prio = calcular_metricas(procesos_prio)

        data = {
            "round_robin": {
                "registro": registro_rr,
                "procesos": [proceso_a_dict(p) for p in procesos_rr],
                "metricas": metricas_rr
            },
            "prioridad": {
                "registro": registro_prio,
                "procesos": [proceso_a_dict(p) for p in procesos_prio],
                "metricas": metricas_prio
            }
        }
        self._send_json(data)

    def _handle_simulacion_integrada(self):
        """Run integrated simulation with FIFO and LRU, return JSON."""
        procesos_fifo = crear_procesos_integrados()
        res_fifo = simular_sistema_completo(
            procesos=procesos_fifo, algoritmo_planif="RR", quantum=3,
            algoritmo_memoria="FIFO", num_marcos_memoria=4,
            lista_archivos=["datos.txt", "config.json", "log.db"]
        )
        metricas_fifo = calcular_metricas(procesos_fifo)

        procesos_lru = crear_procesos_integrados()
        res_lru = simular_sistema_completo(
            procesos=procesos_lru, algoritmo_planif="RR", quantum=3,
            algoritmo_memoria="LRU", num_marcos_memoria=4,
            lista_archivos=["datos.txt", "config.json", "log.db"]
        )
        metricas_lru = calcular_metricas(procesos_lru)

        data = {
            "fifo": {
                "registro": res_fifo["registro"],
                "historial": res_fifo["historial"],
                "fallos_memoria": res_fifo["fallos_memoria"],
                "bitacora_archivos": res_fifo["bitacora_archivos"],
                "procesos": [proceso_a_dict(p) for p in procesos_fifo],
                "metricas": metricas_fifo
            },
            "lru": {
                "registro": res_lru["registro"],
                "historial": res_lru["historial"],
                "fallos_memoria": res_lru["fallos_memoria"],
                "bitacora_archivos": res_lru["bitacora_archivos"],
                "procesos": [proceso_a_dict(p) for p in procesos_lru],
                "metricas": metricas_lru
            }
        }
        self._send_json(data)

    def _send_json(self, data):
        """Send a JSON response."""
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"  Simulador de Sistema Operativo - Frontend")
    print(f"{'='*50}")
    print(f"  Servidor: http://localhost:{PORT}")
    print(f"  Presiona Ctrl+C para detener")
    print(f"{'='*50}\n")

    with http.server.HTTPServer(('', PORT), SimuladorHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
