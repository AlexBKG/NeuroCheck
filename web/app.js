/* NeuroCheck v1.2.0 — UI independiente del compilador Python. */
'use strict';

const $ = (selector) => document.querySelector(selector);
const editor = $('#source-editor');
const exampleSelect = $('#example-select');
const lightButton = $('#light-theme');
const darkButton = $('#dark-theme');
const resultStatus = $('#compile-status');
const phaseContent = $('#phase-content');
const diagramContainer = $('#diagram-container');

let currentResult = null;
let currentPhase = 'tokens';
let compilationEpoch = 0;
let typingTimer;

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
}

function setTheme(mode) {
  const theme = mode === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
  lightButton.setAttribute('aria-pressed', String(theme === 'light'));
  darkButton.setAttribute('aria-pressed', String(theme === 'dark'));
  document.querySelector('meta[name="theme-color"]').content = theme === 'dark' ? '#0d161b' : '#e9eae7';
  try { localStorage.setItem('neurocheck-theme', theme); } catch (_) { /* storage optional */ }
  if (editor.value) compileNow();
}

function showBusy() {
  $('#status-title').textContent = 'Analizando el código...';
  $('#status-description').textContent = 'Comprobando tokens, gramática y dimensiones.';
  $('#status-icon').textContent = '··';
  resultStatus.className = 'result-status';
}

function renderResult(result) {
  currentResult = result;
  $('#token-count').textContent = result.tokens?.length ?? 0;
  $('#error-count').textContent = result.diagnostics?.length ?? 0;
  $('#layer-count').textContent = result.model?.layers?.length ??
    (result.ast?.statements ?? []).filter(item => item.kind === 'capa').length;

  const good = Boolean(result.ok);
  resultStatus.className = 'result-status ' + (good ? 'success' : 'error');
  $('#status-icon').textContent = good ? '✓' : '!';
  $('#status-title').textContent = good ? 'Configuración válida' : 'Se encontraron errores';
  $('#status-description').textContent = good
    ? 'La gramática y las dimensiones de cada capa fueron verificadas.'
    : 'Consulta los diagnósticos y sus sugerencias.';

  $('#model-summary').innerHTML = good
    ? `Red <strong>${escapeHtml(result.model.name)}</strong> · ${result.model.layers.length} capa(s) densa(s).`
    : '';

  const diagnostics = result.diagnostics || [];
  $('#diagnostics').innerHTML = diagnostics.map(d => `
      <div class="diagnostic">
        <strong>${escapeHtml(d.code)} · ${d.line ? `Línea ${Number(d.line)}` : 'Configuración'}</strong>
        <span>${escapeHtml(d.message)}</span>
        ${d.suggestion ? `<small>Recomendación: ${escapeHtml(d.suggestion)}</small>` : ''}
      </div>`).join('');
  renderPhase();
  renderArchitecture();
}

function renderFailure(message) {
  $('#token-count').textContent = '—';
  $('#error-count').textContent = '—';
  $('#layer-count').textContent = '—';
  resultStatus.className = 'result-status error';
  $('#status-icon').textContent = '!';
  $('#status-title').textContent = 'No se pudo analizar el código';
  $('#status-description').textContent = message;
  $('#model-summary').textContent = '';
  $('#diagnostics').textContent = '';
  currentResult = null;
  renderPhase();
  renderArchitecture();
}

async function compileNow() {
  const epoch = ++compilationEpoch;
  showBusy();
  try {
    const response = await fetch('/api/compile', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({source: editor.value, theme: document.documentElement.dataset.theme})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Solicitud inválida');
    if (epoch !== compilationEpoch) return;
    renderResult(data);
  } catch (error) {
    if (epoch !== compilationEpoch) return;
    renderFailure(`Comprueba que el servidor esté activo. Detalle: ${error.message}`);
  }
}

function scheduleCompile() {
  clearTimeout(typingTimer);
  typingTimer = setTimeout(compileNow, 240);
}

function renderTable(rows, columns) {
  if (!rows.length) return '<p class="empty-state">No hay datos disponibles para esta fase.</p>';
  return `<div class="table-wrap"><table class="data-table"><thead><tr>${columns.map(
    col => `<th scope="col">${escapeHtml(col.label)}</th>`).join('')}</tr></thead><tbody>${rows.map(
    row => `<tr>${columns.map(col => `<td>${escapeHtml(row[col.key])}</td>`).join('')}</tr>`
  ).join('')}</tbody></table></div>`;
}

function renderPhase() {
  const data = currentResult;
  if (!data) { phaseContent.innerHTML = '<p class="empty-state">El resultado aparecerá aquí cuando se compile el programa.</p>'; return; }
  if (currentPhase === 'tokens') {
    phaseContent.innerHTML = renderTable(data.tokens || [], [
      {key:'tipo',label:'Tipo'}, {key:'valor',label:'Valor'},
      {key:'linea',label:'Línea'}, {key:'columna',label:'Columna'}
    ]);
  } else if (currentPhase === 'tree') {
    phaseContent.innerHTML = data.parse_tree
      ? `<pre class="code-output">${escapeHtml(data.parse_tree)}</pre>`
      : '<p class="empty-state">El árbol sintáctico se genera al superar la fase de sintaxis.</p>';
  } else if (currentPhase === 'ast') {
    phaseContent.innerHTML = data.ast && Object.keys(data.ast).length
      ? `<pre class="code-output">${escapeHtml(JSON.stringify(data.ast, null, 2))}</pre>`
      : '<p class="empty-state">Aún no existe un AST válido.</p>';
  } else if (currentPhase === 'symbols') {
    phaseContent.innerHTML = renderTable(data.symbols || [], [
      {key:'capa',label:'Capa'}, {key:'entradas',label:'Entradas'},
      {key:'neuronas',label:'Neuronas'}, {key:'pesos declarados',label:'Pesos declarados'},
      {key:'pesos esperados',label:'Pesos esperados'}
    ]);
  }
}

function renderArchitecture() {
  const data = currentResult;
  if (!data?.ok || !data.diagram_svg) {
    diagramContainer.innerHTML = '<p class="empty-state">Corrige los errores de compilación para ver la arquitectura.</p>';
    $('#diagram-note').textContent = '';
    $('#layer-table').innerHTML = '';
    return;
  }
  // SVG se construye en Python a partir de datos validados y etiquetas escapadas.
  diagramContainer.innerHTML = data.diagram_svg;
  $('#diagram-note').textContent = data.diagram_note;
  const rows = [{name:'Entrada', units:data.model.input_dim},
    ...data.model.layers.map(layer => ({name:layer.name, units:layer.units}))];
  $('#layer-table').innerHTML = renderTable(rows, [
    {key:'name',label:'Capa'}, {key:'units',label:'Neuronas'}
  ]);
}

async function loadExample(name) {
  const response = await fetch('/api/example?name=' + encodeURIComponent(name));
  if (!response.ok) throw new Error('No se pudo cargar el ejemplo.');
  const data = await response.json();
  editor.value = data.source;
  await compileNow();
}

function downloadEditor() {
  const blob = new Blob([editor.value], {type:'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'mi_red.neuro';
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

async function initialize() {
  const saved = (() => { try { return localStorage.getItem('neurocheck-theme'); } catch (_) { return null; } })();
  document.documentElement.dataset.theme = saved === 'dark' ? 'dark' : 'light';
  lightButton.setAttribute('aria-pressed', String(saved !== 'dark'));
  darkButton.setAttribute('aria-pressed', String(saved === 'dark'));
  document.querySelector('meta[name="theme-color"]').content = saved === 'dark' ? '#0d161b' : '#e9eae7';
  try {
    const response = await fetch('/api/examples');
    if (!response.ok) throw new Error('No se encontró la lista de ejemplos.');
    const {examples} = await response.json();
    exampleSelect.innerHTML = examples.map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('');
    await loadExample(examples[0]);
  } catch (error) {
    renderFailure(error.message);
  }
}

editor.addEventListener('input', scheduleCompile);
editor.addEventListener('keydown', event => {
  if (event.key === 'Tab') {
    event.preventDefault();
    const start = editor.selectionStart;
    editor.setRangeText('    ', start, editor.selectionEnd, 'end');
    scheduleCompile();
  }
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    clearTimeout(typingTimer);
    compileNow();
  }
});
exampleSelect.addEventListener('change', async event => {
  try { await loadExample(event.target.value); } catch (error) { renderFailure(error.message); }
});
$('#download-btn').addEventListener('click', downloadEditor);
lightButton.addEventListener('click', () => setTheme('light'));
darkButton.addEventListener('click', () => setTheme('dark'));

for (const tab of document.querySelectorAll('[data-tab]')) {
  tab.addEventListener('click', () => {
    const selected = tab.dataset.tab;
    for (const button of document.querySelectorAll('[data-tab]')) {
      const active = button.dataset.tab === selected;
      button.classList.toggle('active', active);
      button.setAttribute('aria-selected', String(active));
    }
    $('#panel-phases').hidden = selected !== 'phases';
    $('#panel-architecture').hidden = selected !== 'architecture';
  });
}
for (const tab of document.querySelectorAll('[data-phase]')) {
  tab.addEventListener('click', () => {
    currentPhase = tab.dataset.phase;
    for (const button of document.querySelectorAll('[data-phase]')) {
      const active = button.dataset.phase === currentPhase;
      button.classList.toggle('active', active);
      button.setAttribute('aria-selected', String(active));
    }
    renderPhase();
  });
}
initialize();
