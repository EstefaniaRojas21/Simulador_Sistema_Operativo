"""
memoria.py - Módulo de Gestión de Memoria
=========================================
Proyecto: Simulador de Sistema Operativo - 2026-1
Integrante 2: Gestión de Memoria
Universidad Pedagógica y Tecnológica de Colombia (UPTC)

Responsabilidades:
    - Simulación de paginación por demanda
    - Algoritmos de reemplazo de páginas: FIFO y LRU
    - Registro de fallos de página
    - Visualización del uso de marcos de página
"""

from typing import List, Dict, Optional, Tuple

class MemoriaFisica:
    """
    Simula la memoria física dividida en marcos de página.
    Gestiona la carga de páginas de procesos en memoria física
    y el reemplazo de páginas mediante FIFO o LRU.
    """
    def __init__(self, numero_marcos: int = 4, algoritmo: str = "FIFO"):
        self.numero_marcos: int = numero_marcos
        self.algoritmo: str = algoritmo.upper()
        # Cada marco almacena una tupla: (pid, numero_pagina) o None
        self.marcos: List[Optional[Tuple[int, int]]] = [None] * numero_marcos
        self.fallos_pagina: int = 0
        
        # Estructuras para los algoritmos de reemplazo
        self.cola_fifo: List[Tuple[int, int]] = []  # Para FIFO: orden de inserción
        self.contador_lru: int = 0
        # Para LRU: mapea (pid, pagina) -> último instante de acceso
        self.accesos_lru: Dict[Tuple[int, int], int] = {}

    def acceder_pagina(self, pid: int, pagina: int, tiempo_actual: int) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Simula el acceso a una página de un proceso.
        
        Retorna:
            (hit, victima):
                - hit (bool): True si la página ya estaba en memoria física,
                             False si ocurrió un fallo de página (Page Fault).
                - victima (tuple o None): Si ocurrió un reemplazo, retorna (pid, pagina)
                                          de la página expulsada, de lo contrario None.
        """
        elemento_buscado = (pid, pagina)
        
        # 1. Verificar si la página ya está cargada (Hit)
        if elemento_buscado in self.marcos:
            if self.algoritmo == "LRU":
                self.accesos_lru[elemento_buscado] = tiempo_actual
            return True, None
            
        # 2. Ocurrió un Fallo de Página (Miss)
        self.fallos_pagina += 1
        victima = None
        
        # Buscar si hay un marco libre
        marco_libre_index = -1
        for idx, marco in enumerate(self.marcos):
            if marco is None:
                marco_libre_index = idx
                break
                
        if marco_libre_index != -1:
            # Hay marcos disponibles, simplemente cargar la página
            self.marcos[marco_libre_index] = elemento_buscado
            if self.algoritmo == "FIFO":
                self.cola_fifo.append(elemento_buscado)
            elif self.algoritmo == "LRU":
                self.accesos_lru[elemento_buscado] = tiempo_actual
        else:
            # Memoria llena: aplicar algoritmo de reemplazo para seleccionar víctima
            if self.algoritmo == "FIFO":
                # La víctima es la primera que se insertó
                victima = self.cola_fifo.pop(0)
            elif self.algoritmo == "LRU":
                # La víctima es la que no se ha usado por más tiempo entre las que están en memoria
                paginas_en_memoria = [m for m in self.marcos if m is not None]
                victima = min(paginas_en_memoria, key=lambda p: self.accesos_lru.get(p, -1))
                if victima in self.accesos_lru:
                    del self.accesos_lru[victima]
            
            # Reemplazar la página víctima en los marcos de memoria
            idx_reemplazo = self.marcos.index(victima)
            self.marcos[idx_reemplazo] = elemento_buscado
            
            if self.algoritmo == "FIFO":
                self.cola_fifo.append(elemento_buscado)
            elif self.algoritmo == "LRU":
                self.accesos_lru[elemento_buscado] = tiempo_actual
                
        return False, victima

    def liberar_paginas_proceso(self, pid: int) -> None:
        """Libera todos los marcos ocupados por un proceso cuando este termina."""
        for idx, marco in enumerate(self.marcos):
            if marco and marco[0] == pid:
                if self.algoritmo == "FIFO" and marco in self.cola_fifo:
                    self.cola_fifo.remove(marco)
                if self.algoritmo == "LRU" and marco in self.accesos_lru:
                    del self.accesos_lru[marco]
                self.marcos[idx] = None

    def obtener_estado_visual(self) -> str:
        """
        Retorna una representación gráfica en cadena del estado actual de los marcos.
        Ejemplo: "[ P1:Pag0 | P2:Pag3 | Vacío | P1:Pag2 ]"
        """
        representaciones = []
        for marco in self.marcos:
            if marco is None:
                representaciones.append("  Vacío  ")
            else:
                pid, pag = marco
                representaciones.append(f" P{pid}:Pag{pag} ")
        return "[" + " | ".join(representaciones) + "]"
