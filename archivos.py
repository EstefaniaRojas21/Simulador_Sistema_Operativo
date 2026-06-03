"""
archivos.py - Módulo de Gestión de Archivos
===========================================
Proyecto: Simulador de Sistema Operativo - 2026-1
Integrante 3: Gestión de Archivos
Universidad Pedagógica y Tecnológica de Colombia (UPTC)

Responsabilidades:
    - Simulación de acceso concurrente a archivos
    - Implementación de bloqueo mutuo (Mutex) para simular exclusión mutua
    - Registro de conflictos de acceso y su resolución
"""

from typing import Dict, List, Optional, Tuple

class ManejadorArchivos:
    """
    Gestiona los bloqueos de archivos virtuales para garantizar la exclusión mutua.
    Mantiene colas de espera para procesos bloqueados debido a colisiones de acceso.
    """
    def __init__(self, lista_archivos: Optional[List[str]] = None):
        if lista_archivos is None:
            lista_archivos = ["datos.txt", "config.json", "log.db"]
        
        # Mapea nombre_archivo -> PID del proceso que tiene el bloqueo (None si está libre)
        self.bloqueos: Dict[str, Optional[int]] = {archivo: None for archivo in lista_archivos}
        # Mapea nombre_archivo -> Lista de PIDs en espera de adquirir el bloqueo
        self.colas_espera: Dict[str, List[int]] = {archivo: [] for archivo in lista_archivos}
        
        # Registro histórico de eventos (conflictos y resoluciones)
        self.bitacora: List[str] = []

    def solicitar_acceso(self, pid: int, archivo: str, tiempo_actual: int) -> bool:
        """
        Intenta adquirir el bloqueo exclusivo (Mutex) para un archivo.
        
        Retorna:
            bool: True si el proceso obtuvo el acceso (o ya lo tenía),
                  False si se produjo un conflicto (archivo bloqueado por otro).
        """
        if archivo not in self.bloqueos:
            # Crear archivo dinámicamente si no existe
            self.bloqueos[archivo] = None
            self.colas_espera[archivo] = []

        propietario = self.bloqueos[archivo]
        
        if propietario is None:
            # Adquirir el bloqueo
            self.bloqueos[archivo] = pid
            msg = f"[{tiempo_actual}] Proceso {pid} bloqueó exitosamente el archivo '{archivo}' (Mutex Adquirido)."
            self.bitacora.append(msg)
            return True
            
        elif propietario == pid:
            # Ya tiene el bloqueo
            return True
            
        else:
            # Conflicto detectado
            if pid not in self.colas_espera[archivo]:
                self.colas_espera[archivo].append(pid)
            msg = (f"[{tiempo_actual}] CONFLICTO: Proceso {pid} intentó acceder a '{archivo}', "
                   f"pero está bloqueado por Proceso {propietario}. Proceso {pid} pasa a lista de espera.")
            if msg not in self.bitacora:  # Evitar duplicar el mismo log en cada unidad de tiempo
                self.bitacora.append(msg)
            return False

    def liberar_archivo(self, pid: int, archivo: str, tiempo_actual: int) -> Optional[int]:
        """
        Libera el bloqueo de un archivo. Si hay procesos en cola, transfiere el bloqueo al siguiente.
        
        Retorna:
            int o None: PID del proceso al que se le concedió el bloqueo a continuación, o None si queda libre.
        """
        if archivo not in self.bloqueos or self.bloqueos[archivo] != pid:
            return None

        self.bloqueos[archivo] = None
        msg_liberacion = f"[{tiempo_actual}] Proceso {pid} liberó el archivo '{archivo}'."
        self.bitacora.append(msg_liberacion)
        
        # Transferir bloqueo si hay procesos esperando
        if self.colas_espera[archivo]:
            siguiente_pid = self.colas_espera[archivo].pop(0)
            self.bloqueos[archivo] = siguiente_pid
            msg_res = (f"[{tiempo_actual}] RESOLUCIÓN: Bloqueo del archivo '{archivo}' "
                       f"concedido a Proceso {siguiente_pid} (siguiente en cola de espera).")
            self.bitacora.append(msg_res)
            return siguiente_pid
            
        return None

    def liberar_todos_los_archivos_proceso(self, pid: int, tiempo_actual: int) -> List[Tuple[str, Optional[int]]]:
        """
        Libera todos los archivos bloqueados por el proceso especificado (útil al terminar el proceso).
        Retorna una lista de tuplas (archivo, siguiente_pid) que indica qué archivos fueron transferidos/liberados.
        """
        transferencias = []
        for archivo, propietario in list(self.bloqueos.items()):
            if propietario == pid:
                sig = self.liberar_archivo(pid, archivo, tiempo_actual)
                transferencias.append((archivo, sig))
            
            # Remover de las colas de espera si el proceso terminó sin obtener el recurso
            if pid in self.colas_espera[archivo]:
                self.colas_espera[archivo].remove(pid)
                
        return transferencias

    def obtener_estado_visual(self) -> Dict[str, str]:
        """Devuelve un estado legible de los archivos para reportar en consola."""
        estado = {}
        for archivo, propietario in self.bloqueos.items():
            prop_str = f"Bloqueado por P{propietario}" if propietario is not None else "Libre"
            espera_str = f"Cola: {[f'P{x}' for x in self.colas_espera[archivo]]}" if self.colas_espera[archivo] else "Cola vacía"
            estado[archivo] = f"{prop_str} | {espera_str}"
        return estado
