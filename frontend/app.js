/**
 * app.js - OS Simulator Frontend Application
 * ============================================
 * Fetches simulation data from the Python API and renders
 * interactive visualizations: Gantt charts, memory frames,
 * file access timelines, and metric dashboards.
 */

/* =========================================================================
   CONSTANTS
   ========================================================================= */

const PROCESS_COLORS = {
    1: '#84a98c', // Sage green - Navegador
    2: '#9fb88d', // Light olive sage - Editor
    3: '#cad2c5', // Pale sage - Compilador
    4: '#a4beb5', // Slate sage - Reproductor
    5: '#c6d5bc', // Light green sage - Antivirus
};

const PROCESS_ICONS = {
    1: '\u{1F310}', // globe
    2: '\u{1F4DD}', // memo
    3: '\u{2699}',  // gear
    4: '\u{1F3B5}', // music
    5: '\u{1F6E1}', // shield
};

const COLOR_CLASSES = ['cyan', 'pink', 'orange', 'green', 'purple', 'yellow'];

/* =========================================================================
   STATE
   ========================================================================= */

let simpleData = null;
let integradaData = null;

/* =========================================================================
   INITIALIZATION
   ========================================================================= */

document.addEventListener('DOMContentLoaded', async () => {
    setupTabs();
    await loadAllData();
    renderDashboard();
    renderCPU();
    renderMemory();
    renderFiles();
});

/* =========================================================================
   TAB SYSTEM
   ========================================================================= */

function setupTabs() {
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            const target = document.getElementById('tab-' + btn.dataset.tab);
            if (target) target.classList.add('active');
        });
    });
}

/* =========================================================================
   DATA LOADING
   ========================================================================= */

async function loadAllData() {
    try {
        const [simple, integrada] = await Promise.all([
            fetch('/api/simulacion-simple').then(r => r.json()),
            fetch('/api/simulacion-integrada').then(r => r.json()),
        ]);
        simpleData = simple;
        integradaData = integrada;

        document.getElementById('loading-indicator').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';
    } catch (err) {
        document.getElementById('loading-indicator').innerHTML =
            '<span style="color:var(--accent-pink);">Error al cargar datos. Aseg\u00FArate de que el servidor est\u00E9 corriendo.</span>';
        console.error('Failed to load simulation data:', err);
    }
}

/* =========================================================================
   DASHBOARD
   ========================================================================= */

function renderDashboard() {
    if (!simpleData || !integradaData) return;

    const rr = simpleData.round_robin;
    const prio = simpleData.prioridad;
    const fifo = integradaData.fifo;
    const lru = integradaData.lru;

    const totalProc = rr.procesos.length;
    const totalTimeRR = Math.max(...rr.procesos.map(p => p.tiempo_fin));
    const totalConflicts = fifo.bitacora_archivos.filter(l => l.includes('CONFLICTO')).length;
    const totalResolutions = fifo.bitacora_archivos.filter(l => l.includes('RESOLUCI')).length;

    let html = '';

    // --- Main Metrics ---
    html += '<h2 class="section-title">Resumen General</h2>';
    html += '<div class="metrics-grid">';
    html += metricCard('cyan', '\u{1F4CB}', totalProc, 'Procesos Simulados');
    html += metricCard('purple', '\u{23F1}', totalTimeRR, 'Tiempo Total (RR)');
    html += metricCard('green', '\u{2705}', rr.metricas.promedio_espera, 'Prom. Espera (RR)');
    html += metricCard('orange', '\u{2705}', prio.metricas.promedio_espera, 'Prom. Espera (Prio)');
    html += metricCard('pink', '\u{26A0}', fifo.fallos_memoria, 'Fallos P\u00E1g. FIFO');
    html += metricCard('yellow', '\u{1F4A1}', lru.fallos_memoria, 'Fallos P\u00E1g. LRU');
    html += '</div>';

    // --- Quick Comparison ---
    html += '<div class="comparison-grid">';

    // RR vs Priority
    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{2699}</span> Round Robin vs Prioridad</div>';
    html += comparisonRow('Prom. Espera', rr.metricas.promedio_espera, prio.metricas.promedio_espera, 30);
    html += comparisonRow('Prom. Retorno', rr.metricas.promedio_retorno, prio.metricas.promedio_retorno, 30);
    html += comparisonRow('Throughput', rr.metricas.throughput, prio.metricas.throughput, 0.25);
    html += '</div>';

    // FIFO vs LRU
    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F4BE}</span> FIFO vs LRU</div>';
    html += comparisonRow('Fallos de P\u00E1gina', fifo.fallos_memoria, lru.fallos_memoria, 30);
    html += comparisonRow('Prom. Espera', fifo.metricas.promedio_espera, lru.metricas.promedio_espera, 30);
    html += comparisonRow('Prom. Retorno', fifo.metricas.promedio_retorno, lru.metricas.promedio_retorno, 30);
    html += '</div>';

    html += '</div>';

    // --- Process Overview ---
    html += '<h2 class="section-title">Procesos del Sistema</h2>';
    html += '<div class="card">';
    html += '<div class="metrics-grid" style="margin-bottom:0">';
    rr.procesos.forEach(p => {
        const color = PROCESS_COLORS[p.pid];
        const icon = PROCESS_ICONS[p.pid] || '\u{1F4E6}';
        html += `<div class="metric-card" style="text-align:left; padding:1rem;">
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <span style="font-size:1.4rem;">${icon}</span>
                <div>
                    <div style="font-weight:700; font-size:0.9rem;">${p.nombre}</div>
                    <span class="pid-badge" style="background:${color}18; color:${color}; border:1px solid ${color}35;">PID ${p.pid}</span>
                </div>
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-muted); line-height:1.8;">
                Duraci\u00F3n: <span style="color:var(--text-primary)">${p.duracion}</span> &middot;
                Prioridad: <span style="color:var(--text-primary)">${p.prioridad}</span> &middot;
                Llegada: <span style="color:var(--text-primary)">${p.tiempo_llegada}</span>
            </div>
        </div>`;
    });
    html += '</div></div>';

    document.getElementById('dashboard-content').innerHTML = html;
}

/* =========================================================================
   CPU SCHEDULING TAB
   ========================================================================= */

function renderCPU() {
    if (!simpleData) return;

    const rr = simpleData.round_robin;
    const prio = simpleData.prioridad;
    let html = '';

    html += '<h2 class="section-title">Planificaci\u00F3n de CPU</h2>';

    // --- Gantt Charts side by side ---
    html += '<div class="comparison-grid mb-2">';

    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F504}</span> Round Robin (quantum = 3)</div>';
    html += buildGanttChart(rr.registro);
    html += '</div>';

    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F3AF}</span> Planificaci\u00F3n por Prioridad</div>';
    html += buildGanttChart(prio.registro);
    html += '</div>';

    html += '</div>';

    // --- Metrics comparison ---
    html += '<div class="vs-divider"><span class="vs-badge">Comparativa de M\u00E9tricas</span></div>';

    html += '<div class="comparison-grid mb-2">';

    // RR Metrics
    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F504}</span> M\u00E9tricas Round Robin</div>';
    html += '<div class="metrics-grid">';
    html += metricCard('cyan', '\u{23F3}', rr.metricas.promedio_espera, 'Prom. Espera');
    html += metricCard('purple', '\u{1F503}', rr.metricas.promedio_retorno, 'Prom. Retorno');
    html += metricCard('green', '\u{26A1}', rr.metricas.throughput, 'Throughput');
    html += metricCard('orange', '\u{1F4C8}', rr.metricas.max_espera, 'M\u00E1x. Espera');
    html += '</div>';
    html += '</div>';

    // Priority Metrics
    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F3AF}</span> M\u00E9tricas Prioridad</div>';
    html += '<div class="metrics-grid">';
    html += metricCard('cyan', '\u{23F3}', prio.metricas.promedio_espera, 'Prom. Espera');
    html += metricCard('purple', '\u{1F503}', prio.metricas.promedio_retorno, 'Prom. Retorno');
    html += metricCard('green', '\u{26A1}', prio.metricas.throughput, 'Throughput');
    html += metricCard('orange', '\u{1F4C8}', prio.metricas.max_espera, 'M\u00E1x. Espera');
    html += '</div>';
    html += '</div>';

    html += '</div>';

    // --- Process Tables ---
    html += '<div class="comparison-grid">';

    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F4CB}</span> Detalle Round Robin</div>';
    html += buildProcessTable(rr.procesos);
    html += '</div>';

    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F4CB}</span> Detalle Prioridad</div>';
    html += buildProcessTable(prio.procesos);
    html += '</div>';

    html += '</div>';

    document.getElementById('cpu-content').innerHTML = html;
}

/* =========================================================================
   MEMORY TAB
   ========================================================================= */

function renderMemory() {
    if (!integradaData) return;

    const fifoHist = integradaData.fifo.historial;
    const lruHist  = integradaData.lru.historial;

    let html = '';
    html += '<h2 class="section-title">Gesti\u00F3n de Memoria \u2014 Paginaci\u00F3n por Demanda</h2>';

    // --- Comparison cards: Page faults ---
    html += '<div class="comparison-grid mb-2">';

    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F504}</span> Reemplazo FIFO</div>';
    html += `<div class="metric-card cyan" style="margin-bottom:1rem;">
        <span class="metric-icon">\u{274C}</span>
        <div class="metric-value">${integradaData.fifo.fallos_memoria}</div>
        <div class="metric-label">Fallos de P\u00E1gina Totales</div>
    </div>`;
    html += '<div class="gantt-label">Diagrama de Gantt (Sim. Integrada FIFO)</div>';
    html += buildGanttChart(integradaData.fifo.registro);
    html += '</div>';

    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F4CA}</span> Reemplazo LRU</div>';
    html += `<div class="metric-card purple" style="margin-bottom:1rem;">
        <span class="metric-icon">\u{274C}</span>
        <div class="metric-value">${integradaData.lru.fallos_memoria}</div>
        <div class="metric-label">Fallos de P\u00E1gina Totales</div>
    </div>`;
    html += '<div class="gantt-label">Diagrama de Gantt (Sim. Integrada LRU)</div>';
    html += buildGanttChart(integradaData.lru.registro);
    html += '</div>';

    html += '</div>';

    // --- Step-through FIFO ---
    html += '<div class="card mb-2">';
    html += '<div class="card-title"><span class="icon">\u{1F50D}</span> Visualizaci\u00F3n Paso a Paso \u2014 FIFO</div>';
    html += `<div class="step-control">
        <button class="step-btn" onclick="memStep('fifo', -1)">\u25C0</button>
        <input type="range" class="step-slider" id="fifo-slider" min="0" max="${fifoHist.length - 1}" value="0"
               oninput="memGoTo('fifo', parseInt(this.value))">
        <button class="step-btn" onclick="memStep('fifo', 1)">\u25B6</button>
        <span class="step-label" id="fifo-step-label">t=0 / ${fifoHist.length - 1}</span>
    </div>`;
    html += '<div id="fifo-frames" class="memory-frames"></div>';
    html += '<div id="fifo-step-info" class="step-info"></div>';
    html += '</div>';

    // --- Step-through LRU ---
    html += '<div class="card mb-2">';
    html += '<div class="card-title"><span class="icon">\u{1F50D}</span> Visualizaci\u00F3n Paso a Paso \u2014 LRU</div>';
    html += `<div class="step-control">
        <button class="step-btn" onclick="memStep('lru', -1)">\u25C0</button>
        <input type="range" class="step-slider" id="lru-slider" min="0" max="${lruHist.length - 1}" value="0"
               oninput="memGoTo('lru', parseInt(this.value))">
        <button class="step-btn" onclick="memStep('lru', 1)">\u25B6</button>
        <span class="step-label" id="lru-step-label">t=0 / ${lruHist.length - 1}</span>
    </div>`;
    html += '<div id="lru-frames" class="memory-frames"></div>';
    html += '<div id="lru-step-info" class="step-info"></div>';
    html += '</div>';

    // --- Trace Table ---
    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F4D6}</span> Trazado Completo \u2014 FIFO</div>';
    html += buildTraceTable(fifoHist);
    html += '</div>';

    document.getElementById('memoria-content').innerHTML = html;

    // Initialize step views
    memGoTo('fifo', 0);
    memGoTo('lru', 0);
}

/* Memory step-through helpers (globally accessible) */
const memStepState = { fifo: 0, lru: 0 };

window.memStep = function(algo, delta) {
    const hist = algo === 'fifo' ? integradaData.fifo.historial : integradaData.lru.historial;
    const next = Math.max(0, Math.min(hist.length - 1, memStepState[algo] + delta));
    memGoTo(algo, next);
};

window.memGoTo = function(algo, step) {
    const hist = algo === 'fifo' ? integradaData.fifo.historial : integradaData.lru.historial;
    memStepState[algo] = step;

    // Update slider
    const slider = document.getElementById(algo + '-slider');
    if (slider) slider.value = step;

    // Update label
    const label = document.getElementById(algo + '-step-label');
    if (label) label.textContent = `t=${hist[step].tiempo} / ${hist.length - 1}`;

    // Render frames
    const framesDiv = document.getElementById(algo + '-frames');
    if (framesDiv) framesDiv.innerHTML = buildMemoryFrames(hist[step].memoria);

    // Render step info
    const infoDiv = document.getElementById(algo + '-step-info');
    if (infoDiv) {
        const s = hist[step];
        const isHit = s.resultado_memoria === 'HIT';
        const resClass = isHit ? 'hit' : 'miss';
        infoDiv.innerHTML = `
            <strong>CPU:</strong> ${escapeHtml(s.cpu)} &nbsp;\u2502&nbsp;
            <strong>P\u00E1gina:</strong> ${s.pagina_solicitada} &nbsp;\u2502&nbsp;
            <strong>Resultado:</strong> <span class="${resClass}">${escapeHtml(s.resultado_memoria)}</span>
        `;
    }
};

/* =========================================================================
   FILES TAB
   ========================================================================= */

function renderFiles() {
    if (!integradaData) return;

    const bitacora = integradaData.fifo.bitacora_archivos;
    const totalConflicts = bitacora.filter(l => l.includes('CONFLICTO')).length;
    const totalResolutions = bitacora.filter(l => l.includes('RESOLUCI')).length;
    const totalLocks = bitacora.filter(l => l.includes('bloque\u00F3 exitosamente')).length;
    const totalReleases = bitacora.filter(l => l.includes('liber\u00F3')).length;

    let html = '';
    html += '<h2 class="section-title">Gesti\u00F3n de Archivos \u2014 Acceso Concurrente con Mutex</h2>';

    // Metrics
    html += '<div class="metrics-grid mb-2">';
    html += metricCard('cyan', '\u{1F512}', totalLocks, 'Bloqueos Adquiridos');
    html += metricCard('pink', '\u{26A0}', totalConflicts, 'Conflictos Detectados');
    html += metricCard('green', '\u{2705}', totalResolutions, 'Resoluciones');
    html += metricCard('orange', '\u{1F513}', totalReleases, 'Liberaciones');
    html += '</div>';

    // File info
    html += '<div class="card mb-2">';
    html += '<div class="card-title"><span class="icon">\u{1F4C2}</span> Archivos del Sistema</div>';
    html += '<div class="metrics-grid" style="margin-bottom:0">';
    ['datos.txt', 'config.json', 'log.db'].forEach((f, i) => {
        const colors = ['cyan', 'orange', 'purple'];
        const icons = ['\u{1F4C4}', '\u{2699}', '\u{1F4CA}'];
        html += `<div class="metric-card ${colors[i]}">
            <span class="metric-icon">${icons[i]}</span>
            <div class="metric-value" style="font-size:1rem;">${f}</div>
            <div class="metric-label">Archivo con Mutex</div>
        </div>`;
    });
    html += '</div></div>';

    // Timeline
    html += '<div class="card">';
    html += '<div class="card-title"><span class="icon">\u{1F4DC}</span> Bit\u00E1cora de Eventos</div>';
    html += buildTimeline(bitacora);
    html += '</div>';

    document.getElementById('archivos-content').innerHTML = html;
}

/* =========================================================================
   COMPONENT BUILDERS
   ========================================================================= */

/** Build a Gantt chart from a registro array */
function buildGanttChart(registro) {
    if (!registro || !registro.length) return '<p class="text-muted">Sin datos</p>';

    const totalTime = registro[registro.length - 1].fin;
    let html = '<div class="gantt-wrapper">';

    // Bars
    html += '<div class="gantt-chart">';
    registro.forEach(entry => {
        const widthPct = (entry.duracion_turno / totalTime) * 100;
        const color = PROCESS_COLORS[entry.pid] || '#888';
        html += `<div class="gantt-bar" style="width:${widthPct}%; background:${color};">
            P${entry.pid}(${entry.duracion_turno})
            <span class="gantt-tooltip">
                <strong>${entry.nombre}</strong> (PID ${entry.pid})<br>
                t=${entry.inicio} \u2192 t=${entry.fin} &nbsp;|&nbsp; ${entry.duracion_turno} u.t.
            </span>
        </div>`;
    });
    html += '</div>';

    // Time axis
    html += '<div class="gantt-time-axis">';
    registro.forEach(entry => {
        const widthPct = (entry.duracion_turno / totalTime) * 100;
        html += `<span style="width:${widthPct}%">${entry.inicio}</span>`;
    });
    html += `<span class="gantt-time-end">${totalTime}</span>`;
    html += '</div>';

    html += '</div>';
    return html;
}

/** Build a process detail table */
function buildProcessTable(procesos) {
    let html = '<div class="table-wrapper"><table class="process-table"><thead><tr>';
    html += '<th>PID</th><th>Nombre</th><th>Llegada</th><th>Duraci\u00F3n</th>';
    html += '<th>Prioridad</th><th>Espera</th><th>Ejec.</th><th>Retorno</th><th>Estado</th>';
    html += '</tr></thead><tbody>';

    [...procesos].sort((a, b) => a.pid - b.pid).forEach(p => {
        const color = PROCESS_COLORS[p.pid] || '#888';
        html += '<tr>';
        html += `<td><span class="pid-badge" style="background:${color}15; color:${color}; border:1px solid ${color}30;">P${p.pid}</span></td>`;
        html += `<td style="font-family:var(--font-body); font-weight:500;">${p.nombre}</td>`;
        html += `<td>${p.tiempo_llegada}</td>`;
        html += `<td>${p.duracion}</td>`;
        html += `<td>${p.prioridad}</td>`;
        html += `<td>${p.tiempo_espera}</td>`;
        html += `<td>${p.tiempo_ejecucion}</td>`;
        html += `<td>${p.tiempo_retorno}</td>`;
        html += `<td><span class="badge badge-success">${p.estado}</span></td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    return html;
}

/** Build memory frame visualization from a visual string */
function buildMemoryFrames(memStr) {
    const frames = parseMemoryState(memStr);
    let html = '';
    frames.forEach((frame, i) => {
        if (frame.empty) {
            html += `<div class="memory-frame empty">
                <span class="frame-label">Marco ${i}</span>
                Vac\u00EDo
            </div>`;
        } else {
            const color = PROCESS_COLORS[frame.pid] || '#888';
            html += `<div class="memory-frame filled" style="border-color:${color}80; background:${color}12; color:${color};">
                <span class="frame-label" style="color:${color}90;">Marco ${i}</span>
                <strong>P${frame.pid}:P\u00E1g${frame.page}</strong>
            </div>`;
        }
    });
    return html;
}

/** Build trace table for memory step history */
function buildTraceTable(historial) {
    let html = '<div class="table-wrapper"><table class="process-table"><thead><tr>';
    html += '<th>Tiempo</th><th>CPU</th><th>P\u00E1g.</th><th>Resultado</th><th>Marcos de Memoria</th>';
    html += '</tr></thead><tbody>';

    historial.forEach(step => {
        const isHit = step.resultado_memoria === 'HIT';
        const resStyle = isHit
            ? 'color:var(--accent-green); font-weight:600;'
            : 'color:var(--accent-pink); font-weight:600;';

        html += '<tr>';
        html += `<td>${step.tiempo}</td>`;
        html += `<td style="font-family:var(--font-body);">${escapeHtml(step.cpu)}</td>`;
        html += `<td>${step.pagina_solicitada}</td>`;
        html += `<td style="${resStyle}">${escapeHtml(step.resultado_memoria)}</td>`;
        html += `<td style="font-size:0.7rem;">${escapeHtml(step.memoria)}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    return html;
}

/** Build timeline from bitacora strings */
function buildTimeline(bitacora) {
    if (!bitacora.length) return '<p class="text-muted">Sin eventos</p>';

    let html = '<div class="timeline">';
    bitacora.forEach(entry => {
        let type = 'lock';
        let icon = '\u{1F512}';
        if (entry.includes('CONFLICTO')) { type = 'conflict'; icon = '\u{26A0}'; }
        else if (entry.includes('RESOLUCI')) { type = 'resolution'; icon = '\u{2705}'; }
        else if (entry.includes('liber\u00F3')) { type = 'release'; icon = '\u{1F513}'; }

        // Extract time from "[X] ..."
        const timeMatch = entry.match(/^\[(\d+)\]/);
        const time = timeMatch ? timeMatch[1] : '?';
        const text = entry.replace(/^\[\d+\]\s*/, '');

        html += `<div class="timeline-item ${type}">
            <div class="timeline-time">${icon} t = ${time}</div>
            <div class="timeline-text">${highlightProcesses(escapeHtml(text))}</div>
        </div>`;
    });
    html += '</div>';
    return html;
}

/* =========================================================================
   HELPERS
   ========================================================================= */

/** Create a single metric card */
function metricCard(colorClass, icon, value, label) {
    return `<div class="metric-card ${colorClass}">
        <span class="metric-icon">${icon}</span>
        <div class="metric-value">${value}</div>
        <div class="metric-label">${label}</div>
    </div>`;
}

/** Create a comparison row with dual progress bars */
function comparisonRow(label, val1, val2, maxVal) {
    const max = maxVal || Math.max(val1, val2) || 1;
    const pct1 = Math.min((val1 / max) * 100, 100);
    const pct2 = Math.min((val2 / max) * 100, 100);

    return `<div class="progress-bar-wrapper">
        <div class="progress-bar-label">
            <span class="label-name">${label}</span>
            <span class="label-value">${val1} vs ${val2}</span>
        </div>
        <div class="progress-bar" style="margin-bottom:4px;">
            <div class="progress-bar-fill" style="width:${pct1}%; background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));"></div>
        </div>
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width:${pct2}%; background: linear-gradient(90deg, var(--accent-orange), var(--accent-pink));"></div>
        </div>
    </div>`;
}

/** Parse the visual memory string into structured data */
function parseMemoryState(str) {
    if (!str) return [];
    // Format: "[ P1:Pag0 |  Vacío  | P2:Pag3 | P1:Pag2 ]"
    const inner = str.slice(1, -1); // Remove [ and ]
    return inner.split('|').map(s => {
        s = s.trim();
        if (!s || s === 'Vac\u00EDo') return { empty: true };
        const match = s.match(/P(\d+):Pag(\d+)/);
        if (match) return { pid: parseInt(match[1]), page: parseInt(match[2]), empty: false };
        return { empty: true };
    });
}

/** Escape HTML special characters */
function escapeHtml(str) {
    if (typeof str !== 'string') return String(str);
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;');
}

/** Highlight "Proceso N" mentions in text */
function highlightProcesses(text) {
    return text.replace(/Proceso (\d+)/g, (match, pid) => {
        const color = PROCESS_COLORS[parseInt(pid)] || 'var(--text-primary)';
        return `<strong style="color:${color}">Proceso ${pid}</strong>`;
    });
}
