# Simulador de Sistema Operativo - UPTC

Este proyecto es un **Simulador de Sistema Operativo** interactivo diseñado para el curso de Sistemas Operativos de la Universidad Pedagógica y Tecnológica de Colombia (UPTC). El simulador modela en tiempo real los tres pilares fundamentales de la gestión de recursos de un SO:
1.  **Planificación de CPU (Procesador):** Algoritmos Round Robin y Planificación por Prioridad.
2.  **Gestión de Memoria:** Paginación por demanda y algoritmos de reemplazo de páginas (FIFO y LRU).
3.  **Gestión de Archivos Concurrente:** Exclusión mutua (Mutex) para simular colisiones y colas de bloqueo de archivos.

El proyecto está construido con un **Backend en Python** (servidor local y motores de simulación) y un **Frontend Web interactivo** en HTML, CSS (tema claro de tonos salvia y forestales) y Javascript vainilla.

---

## 🚀 Cómo Ejecutar el Simulador

### Prerrequisitos
*   Tener instalado Python (versión 3.8 o superior).

### Paso 1: Iniciar el Servidor Backend
Abre una terminal o consola de comandos en la carpeta raíz del proyecto y ejecuta:
```bash
python server.py
```
El servidor levantará un servicio local HTTP en el puerto `8080` e iniciará los motores de simulación. Verás el siguiente mensaje en consola:
```text
==================================================
  Simulador de Sistema Operativo - Frontend
==================================================
  Servidor: http://localhost:8080
  Presiona Ctrl+C para detener
==================================================
```

### Paso 2: Abrir el Dashboard Web
Abre tu navegador de preferencia (Chrome, Edge, Firefox, etc.) e ingresa a la siguiente dirección:
*   [http://localhost:8080](http://localhost:8080)

Allí podrás interactuar con las diferentes pestañas: **Dashboard**, **Planificación CPU**, **Memoria** y **Archivos**.

---

## 🧪 Cómo Ejecutar las Pruebas Unitarias

El backend cuenta con una suite completa de **146 pruebas de consistencia y validación** para garantizar que los planificadores y las colas funcionen exactamente bajo las reglas teóricas de sistemas operativos.

Para correr las pruebas unitarias, ejecuta en tu terminal:
```bash
python -X utf8 test_process.py
```

---

## 📂 Estructura del Proyecto

El código fuente está distribuido de la siguiente forma:

*   `procesos.py`: Contiene el motor principal de planificación de CPU. Define la estructura de datos del `Proceso`, la clase `ColaProcesos` y los algoritmos de planificación Round Robin y Prioridad. Además, integra la simulación completa combinando CPU, memoria y Mutex.
*   `memoria.py`: Módulo de gestión de memoria física. Implementa la clase `MemoriaFisica` que simula la carga de páginas en marcos físicos y los algoritmos de reemplazo FIFO y LRU.
*   `archivos.py`: Módulo de gestión de concurrencia y exclusión mutua. Implementa el gestor de bloqueos (Mutex) y maneja las colas de espera en caso de conflictos por acceso concurrente a los archivos.
*   `server.py`: Servidor HTTP en Python. Sirve los archivos estáticos de la interfaz web y expone las rutas API `/api/simulacion-simple` y `/api/simulacion-integrada` que devuelven los resultados lógicos en formato JSON.
*   `frontend/`: Carpeta que contiene la interfaz del usuario:
    *   `index.html`: Estructura HTML del dashboard.
    *   `styles.css`: Estilos visuales del tema claro profesional (paleta verde salvia).
    *   `app.js`: Script de cliente que consume la API del servidor y renderiza los diagramas de Gantt, la visualización paso a paso de la memoria y la bitácora de Mutex.

---

## ⚙️ Conceptos Teóricos Simulados

### 1. Planificación de CPU
*   **Round Robin (RR):** Algoritmo equitativo basado en el tiempo. Cada proceso dispone de un tiempo máximo en CPU (Quantum) antes de ser expulsado y reenviado al final de la cola de listos.
*   **Prioridad (No Expulsivo):** El procesador corre de inicio a fin el proceso listo con prioridad más alta. Los empates se resuelven por orden de llegada (FCFS).

### 2. Gestión de Memoria
*   **Paginación por Demanda:** Las páginas virtuales del código de un proceso se cargan en marcos de memoria física únicamente cuando el hilo del procesador solicita ejecutarlas.
*   **Fallo de Página (Page Fault):** Ocurre cuando el procesador requiere leer una página que no se encuentra mapeada en la RAM física, obligando al sistema a cargarla desde el disco.
*   **Algoritmo FIFO:** Expulsa el marco de página que primero ingresó a la RAM física.
*   **Algoritmo LRU:** Expulsa la página que lleva más tiempo sin ser leída por la CPU.

### 3. Exclusión Mutua (Mutex)
*   Para evitar colisiones o corrupción, los archivos del sistema simulado (`datos.txt`, `config.json`, `log.db`) implementan un cerrojo exclusivo (Mutex). Si un proceso intenta acceder a un archivo bloqueado, pasa al estado `BLOQUEADO` y se almacena en la cola del recurso hasta que el propietario actual libere el archivo.

---

## 👥 Créditos y Autores
Proyecto Final desarrollado para la asignatura de **Sistemas Operativos** - UPTC.
