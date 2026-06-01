#!/usr/bin/env python3
"""
gen_moea.py — Generate HW1_KR.ipynb
Replaces MOEA cells with auto-extracted templates from moea_module.py
Also enhances sections 1 and 2.
"""

import json, sys, os, inspect, re
import moea_module
from pathlib import Path

SRC = inspect.getsource(moea_module)

def _extract_func(name):
    """Extract a function body from moea_module source by name."""
    import re
    # find start: 'def name('
    start = SRC.find(f'def {name}(')
    if start == -1:
        raise ValueError(f'Function {name} not found in moea_module.py')
    # find the colon at end of signature (may span multiple lines)
    sig_end = SRC.find('\n    """', start)
    if sig_end == -1:
        sig_end = SRC.find('\n    #', start)
    if sig_end == -1:
        sig_end = SRC.index('\ndef ', start)
    sig_end = SRC.index(':', start, sig_end) + 1  # include the :
    # scan body lines: lines starting with indent spaces or blank
    body_start = sig_end
    body_end = body_start
    lines = SRC[body_start:].split('\n')
    for line in lines:
        stripped = line.rstrip()
        if stripped == '' or stripped.startswith(('    ', '\t')):
            body_end += len(line) + 1  # +1 for newline
            continue
        break
    return SRC[start:body_end].rstrip()

def _extract_class(name):
    """Extract a class body from moea_module source by name (with all methods)."""
    import re
    start = SRC.find(f'class {name}')
    if start == -1:
        raise ValueError(f'Class {name} not found in moea_module.py')
    # find the colon at end of class line
    sig_end = SRC.index(':', start) + 1
    # scan body lines: lines starting with indent spaces or blank
    body_end = sig_end
    lines = SRC[body_end:].split('\n')
    for line in lines:
        stripped = line.rstrip()
        if stripped == '' or stripped.startswith(('    ', '\t')):
            body_end += len(line) + 1
            continue
        break
    return SRC[start:body_end].rstrip()

with open('HW1_JR.ipynb', 'r') as f:
    nb = json.load(f)

# ── Helpers ──
def code(lines, ids=None):
    """Create a code cell from list of lines or single string."""
    if isinstance(lines, str):
        # Preserve newlines between source lines
        src_lines = lines.split('\n')
        source = [l + '\n' for l in src_lines]
    else:
        source = [l if l.endswith('\n') else l + '\n' for l in lines]
    cell = {
        'cell_type': 'code',
        'metadata': {},
        'execution_count': None,
        'outputs': [],
        'source': source,
    }
    if ids:
        cell['id'] = ids
    return cell

def md(text):
    """Create a markdown cell."""
    return {
        'cell_type': 'markdown',
        'metadata': {},
        'source': text.split('\n') if isinstance(text, str) else list(text),
    }

# ── Enhanced sections 1 and 2 ──

new_section1 = md('''\
<h1 id="1-ordenes-y-conos" style="border-bottom: 1px solid #ccc;">1. Órdenes y conos</h1>

## 1.1 (10 Puntos)

Sea $\\|\\cdot\\| : \\mathbb{R}^m \\to \\mathbb{R}_0^+$ una norma arbitraria. Definimos la relación binaria:
$$
x \\leq_{\\|\\cdot\\|} y \\iff \\|x\\| \\leq \\|y\\|.
$$

---
### Preorden y conexidad de la relación inducida por la norma

Para determinar si $\\leq_{\\|\\cdot\\|}$ constituye un **orden parcial**, debe satisfacer tres propiedades: reflexividad, transitividad y antisimetría.

**Reflexividad:** Para todo $x \\in \\mathbb{R}^m$, se cumple $\\|x\\| \\leq \\|x\\|$, por lo tanto $x \\leq_{\\|\\cdot\\|} x$. La relación es reflexiva.

**Transitividad:** Si $x \\leq_{\\|\\cdot\\|} y$ y $y \\leq_{\\|\\cdot\\|} z$, entonces $\\|x\\| \\leq \\|y\\|$ y $\\|y\\| \\leq \\|z\\|$. Por transitividad del orden usual en $\\mathbb{R}$, se tiene $\\|x\\| \\leq \\|z\\|$, luego $x \\leq_{\\|\\cdot\\|} z$. La relación es transitiva.

**Antisimetría:** Si $x \\leq_{\\|\\cdot\\|} y$ y $y \\leq_{\\|\\cdot\\|} x$, entonces $\\|x\\| = \\|y\\|$. Sin embargo, la igualdad de normas **no implica** la igualdad de vectores cuando $m \\geq 2$. En cualquier espacio de dimensión $m \\geq 2$, el conjunto de vectores con norma igual a una constante $c > 0$ define una hiperesfera de dimensión $m-1$, la cual contiene infinitos vectores distintos.

Por ejemplo, en $\\mathbb{R}^2$ con la norma euclidiana $\\|\\cdot\\|_2$, consideremos:
$$
x = (1, 0)^T,\\qquad y = (0, 1)^T.
$$
Calculando sus normas:
$$
\\|x\\|_2 = \\sqrt{1^2 + 0^2} = 1,\\qquad \\|y\\|_2 = \\sqrt{0^2 + 1^2} = 1.
$$
Ambas relaciones $x \\leq_{\\|\\cdot\\|_2} y$ y $y \\leq_{\\|\\cdot\\|_2} x$ se satisfacen simultáneamente, pero $x \\neq y$. Esta falla es general para cualquier norma en $\\mathbb{R}^m$ cuando $m \\geq 2$. **La relación no es antisimétrica**.

**Conclusión:** $\\leq_{\\|\\cdot\\|}$ **NO** es un orden parcial. Al satisfacer solo reflexividad y transitividad, se clasifica como un **preorden** (o cuasi-orden).

---
### Conexidad (totalidad)

Una relación es **conectada** (u orden total) si para cualquier par $x, y \\in \\mathbb{R}^m$, se cumple $x \\leq_{\\|\\cdot\\|} y$ o $y \\leq_{\\|\\cdot\\|} x$. Dado que la norma mapea todo vector a un escalar en $\\mathbb{R}_0^+$, y el orden usual $\\leq$ en $\\mathbb{R}$ es total, siempre se cumple $\\|x\\| \\leq \\|y\\|$ o $\\|y\\| \\leq \\|x\\|$. **La relación es conectada**.

Por lo tanto, $\\leq_{\\|\\cdot\\|}$ es un **preorden total** (orden débil).

---
### Cono local de direcciones de mejora

Las direcciones de mejora local de este preorden se analizan mediante el cono de direcciones de mejora $\\mathcal{C}_{\\leq_{\\|\\cdot\\|}}(y)$ en un punto $y \\neq 0$. Este cono comprende todas las direcciones $d \\in \\mathbb{R}^m$ para las cuales existe un escalar positivo $\\bar{t} > 0$ tal que:
$$
\\|y + t d\\| \\leq \\|y\\| \\quad \\forall t \\in (0, \\bar{t}].
$$

Usando la norma euclidiana $\\|\\cdot\\|_2$, elevamos al cuadrado para simplificar:
$$
\\|y + t d\\|_2^2 \\leq \\|y\\|_2^2 \\iff \\langle y + t d,\\, y + t d \\rangle \\leq \\langle y,\\, y \\rangle.
$$

Expandiendo el producto interior:
$$
\\langle y,\\, y \\rangle + 2t \\langle y,\\, d \\rangle + t^2 \\langle d,\\, d \\rangle \\leq \\langle y,\\, y \\rangle
\\iff 2t \\langle y,\\, d \\rangle + t^2 \\|d\\|_2^2 \\leq 0.
$$

Dividiendo entre $t > 0$:
$$
2 \\langle y,\\, d \\rangle + t \\|d\\|_2^2 \\leq 0.
$$

Para que esta desigualdad se cumpla para todo $t \\in (0, \\bar{t}]$ con algún $\\bar{t} > 0$, el límite cuando $t \\to 0^+$ debe satisfacer $\\langle y,\\, d \\rangle \\leq 0$. Si $\\langle y,\\, d \\rangle < 0$, siempre existe un $\\bar{t} = -2\\langle y,\\, d \\rangle / \\|d\\|_2^2 > 0$ que satisface la desigualdad estrictamente. Si $\\langle y,\\, d \\rangle = 0$, la desigualdad se reduce a $t \\|d\\|_2^2 \\leq 0$, lo cual solo es posible si $d = 0$.

Por lo tanto, el cono de direcciones de mejora local en un punto $y \\neq 0$ es:
$$
\\mathcal{C}_{\\leq_{\\|\\cdot\\|_2}}(y) = \\{ d \\in \\mathbb{R}^m \\mid \\langle y,\\, d \\rangle < 0 \\} \\cup \\{0\\}.
$$

Geométricamente, este cono representa un **semiespacio abierto** orientado en la dirección opuesta al vector $y$, junto con el origen. Esta estructura forma un cono convexo y puntiagudo. En el origen ($y = 0$), la desigualdad se simplifica a $t^2 \\|d\\|_2^2 \\leq 0$, que solo se satisface cuando $d = 0$, es decir, $\\mathcal{C}_{\\leq_{\\|\\cdot\\|_2}}(0) = \\{0\\}$.\
''')

new_section2 = md('''\
<h1 id="2-asf-y-cono-de-direcciones-de-mejora" style="border-bottom: 1px solid #ccc;">2. ASF y cono de direcciones de mejora</h1>

## 2.1 (15 Puntos)

Sea la *Achievement Scalarizing Function* (ASF) de Chebyshev:
$$
s(x; w) = \\max_{i=1,\\ldots,m} \\left\\{ \\frac{x_i}{w_i} \\right\\}, \\quad w \\in \\mathbb{R}^m_{++},\\; w_i > 0.
$$

Definimos la relación binaria:
$$
x \\leq_s y \\iff s(x; w) \\leq s(y; w).
$$

---
### Cono global de direcciones de mejora

El cono global de direcciones de mejora $\\mathcal{C}_{\\leq_s}$ se construye con respecto al origen. Representa el conjunto de direcciones $d \\in \\mathbb{R}^m$ que mejoran el origen. Como $s(0; w) = 0$, una dirección $d$ pertenece al cono global de mejora si y solo si:
$$
s(d; w) \\leq 0 \\iff \\max_{i=1,\\ldots,m} \\left\\{ \\frac{d_i}{w_i} \\right\\} \\leq 0.
$$

Dado que los pesos $w_i$ son estrictamente positivos, el máximo es no positivo si y solo si cada coordenada de $d$ es no positiva:
$$
\\frac{d_i}{w_i} \\leq 0 \\iff d_i \\leq 0 \\quad \\forall i = 1,\\ldots,m.
$$

Esto produce el cono de ordenamiento global:
$$
\\mathcal{C}_{\\leq_s} = \\{ d \\in \\mathbb{R}^m \\mid d_i \\leq 0 \\; \\forall i \\} = \\mathbb{R}^{m}_{-}.
$$

El cono global de direcciones de mejora es el **ortante no positivo** del espacio $m$-dimensional.

Para el caso bidimensional ($m = 2$), el cono de mejora global $\\mathcal{C}_{\\leq_s}$ se visualiza en el plano cartesiano como el cuadrante inferior izquierdo. Las fronteras de este cono son el eje $x_1$ no positivo y el eje $x_2$ no positivo, con su vértice en el origen. Cualquier vector dirección $d$ dentro de este cuadrante (incluyendo las fronteras) garantiza que ninguno de los objetivos escalados aumente.

---
### (a) $\\mathcal{C}_{\\leq_s}$ es convexo

Sean $d^{1}, d^{2} \\in \\mathcal{C}_{\\leq_s}$ y sea $\\lambda \\in [0,1]$. Por definición del ortante no positivo, las componentes satisfacen $d^{1}_i \\leq 0$ y $d^{2}_i \\leq 0$ para todo $i = 1,\\ldots,m$.

Para la combinación convexa $d^{\\lambda} = \\lambda d^{1} + (1 - \\lambda) d^{2}$, la $i$-ésima coordenada es:
$$
d^{\\lambda}_i = \\lambda d^{1}_i + (1 - \\lambda) d^{2}_i.
$$

Como $\\lambda \\geq 0$ y $1 - \\lambda \\geq 0$, ambos términos son no positivos, y su suma también es no positiva. Por lo tanto, $d^{\\lambda}_i \\leq 0$ para todo $i$, lo que implica $d^{\\lambda} \\in \\mathcal{C}_{\\leq_s}$. **El cono es convexo**.

---
### (b) $\\mathcal{C}_{\\leq_s}$ es puntiagudo

Un cono $C$ es puntiagudo si no contiene rectas, lo que equivale a que su intersección con su opuesto contenga solo el origen: $C \\cap (-C) = \\{0\\}$.

Para $\\mathcal{C}_{\\leq_s} = \\mathbb{R}^{m}_{-}$, su opuesto es $-\\mathcal{C}_{\\leq_s} = \\mathbb{R}^{m}_{+}$. Evaluando su intersección:
$$
\\mathcal{C}_{\\leq_s} \\cap (-\\mathcal{C}_{\\leq_s}) = \\mathbb{R}^{m}_{-} \\cap \\mathbb{R}^{m}_{+}
= \\{ d \\in \\mathbb{R}^m \\mid d_i \\leq 0 \\text{ y } d_i \\geq 0 \\; \\forall i \\} = \\{0\\}.
$$

El único vector que satisface simultáneamente ambas desigualdades para toda coordenada es $d_i = 0$ para todo $i$. **El cono es puntiagudo**.

---
### (c) Tipo de orden inducido por $\\leq_s$

Analizamos las propiedades algebraicas de la relación $x \\leq_s y \\iff s(x; w) \\leq s(y; w)$:

- **Reflexividad:** $s(x; w) \\leq s(x; w)$ se cumple para todo $x \\in \\mathbb{R}^m$.
- **Transitividad:** Si $s(x; w) \\leq s(y; w)$ y $s(y; w) \\leq s(z; w)$, entonces $s(x; w) \\leq s(z; w)$ por transitividad de $\\leq$ en $\\mathbb{R}$.
- **Conexidad:** Para todo $x, y \\in \\mathbb{R}^m$, los valores $s(x; w)$ y $s(y; w)$ son números reales, y $\\leq$ en $\\mathbb{R}$ es conexo.
- **Antisimetría:** Si $x \\leq_s y$ y $y \\leq_s x$, entonces $s(x; w) = s(y; w)$. Esta igualdad **no implica** $x = y$.

Por ejemplo, en $\\mathbb{R}^2$ con $w = (1, 1)^T$, sean $x = (1, 0)^T$ y $y = (1, 1)^T$:
$$
s(x; w) = \\max\\left\\{\\frac{1}{1},\\; \\frac{0}{1}\\right\\} = 1,\\qquad
s(y; w) = \\max\\left\\{\\frac{1}{1},\\; \\frac{1}{1}\\right\\} = 1.
$$
Ambas relaciones se satisfacen, pero $x \\neq y$. **La relación no es antisimétrica**.

**Conclusión:** $\\leq_s$ induce un **preorden total** (orden débil) en $\\mathbb{R}^m$.\
''')

cone_viz = code('''\
# Visualizaci\\\'on del cono de mejora global $\\mathcal{C}_{\\leq_s} = \\mathbb{R}^2_-$
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(7, 7))

# Cono: ortante no positivo como pol\\\'igono (desde origen)
cone_verts = [(0, 0), (-3, 0), (-3, -3), (0, -3)]
cone = Polygon(cone_verts, closed=True, color='steelblue', alpha=0.2,
               label=r'$\\mathcal{C}_{\\leq_s} = \\mathbb{R}^2_-$')
ax.add_patch(cone)

# Ejes coordenados
ax.axhline(0, color='black', linewidth=0.8)
ax.axvline(0, color='black', linewidth=0.8)

# Flechas de direcciones de mejora
for dx, dy in [(-1, 0), (0, -1), (-0.7, -0.7), (-2.0, -0.5), (-0.5, -2.0), (-1.5, -1.5)]:
    ax.arrow(0, 0, dx, dy, head_width=0.12, head_length=0.12,
             fc='crimson', ec='crimson', alpha=0.8, length_includes_head=True)

# Frontera del cono
ax.plot([-3, 0], [0, 0], color='darkblue', linewidth=2.5, linestyle='--', label='Frontera del cono')
ax.plot([0, 0], [-3, 0], color='darkblue', linewidth=2.5, linestyle='--')

ax.plot(0, 0, 'ko', markersize=8)
ax.text(-2.0, -1.5, r'$d_1 \\leq 0,\\; d_2 \\leq 0$', fontsize=12,
        ha='center', va='center', style='italic',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

ax.set_xlim(-3.5, 2.0)
ax.set_ylim(-3.5, 2.0)
ax.set_xlabel('$d_1$', fontsize=13)
ax.set_ylabel('$d_2$', fontsize=13)
ax.set_title(r'Cono de mejora global $\\mathcal{C}_{\\leq_s}$ para $m=2$', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10, loc='lower right')
ax.set_aspect('equal')
plt.tight_layout()
plt.show()
print(r'Cono de mejora global: ortante no positivo $\\mathbb{R}^2_-$')\
''')

# ── MOEA cells (auto-extracted from moea_module) ──
new = []

# Pymoo setup cell (imports needed by extracted cells)
new.append(code('''\
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.survival import Survival
from pymoo.core.problem import Problem
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
from pymoo.optimize import minimize
from pymoo.indicators.hv import HV
from pymoo.problems import get_problem
print("Pymoo imports loaded.")\
'''))

# Utility functions
new.append(code(_extract_func('riesz_energy_matrix')))
new.append(code(_extract_func('normalize_objectives')))
new.append(code(_extract_func('greedy_rse_removal')))
new.append(code(_extract_func('dominates_pareto')))
new.append(code(_extract_func('dominates_one_minus_k')))
new.append(code(_extract_func('fast_non_dominated_sort')))
new.append(code(_extract_func('crowding_distance')))

# Standard n_var helper (used by make_problem)
new.append(code(_extract_func('standard_n_var')))

# Survival classes
new.append(code(_extract_class('RSESurvival')))
new.append(code(_extract_class('RelationSurvival')))

# Algorithm classes
new.append(code(_extract_class('RSENSGA2')))
new.append(code(_extract_class('RelNSGA2')))

# Custom problem classes (used by make_problem)
new.append(code(_extract_class('IDTLZ1')))
new.append(code(_extract_class('IDTLZ2')))

# Problem factory
new.append(code(_extract_func('make_problem')))
new.append(code(_extract_func('build_reference_point')))
new.append(code(_extract_func('make_algorithm')))

# RunResult dataclass + _get_problem_cached
new.append(code('''\
from dataclasses import dataclass
import numpy as np

@dataclass
class RunResult:
    problem: str
    m: int
    algorithm: str
    seed: int
    hv: float
    F: np.ndarray
    exec_time_ms: float
    hv_time_ms: float = 0.0

_problem_cache = {}
def _get_problem_cached(name, m):
    key = (name, m)
    if key not in _problem_cache:
        _problem_cache[key] = make_problem(name, m)
    return _problem_cache[key]\
'''))

# Benchmark runner
new.append(code(_extract_func('_moea_worker')))
new.append(code(_extract_func('run_moea_benchmark')))

# Plotting
new.append(code('''\
# Plot functions
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def plot_hv_boxplots(df_runs):
    """Boxplots of HV per (problem, m, algorithm)."""
    import matplotlib.pyplot as plt
    problems = df_runs['problem'].unique()
    for prob in problems:
        sub = df_runs[df_runs['problem'] == prob]
        ms = sorted(sub['m'].unique())
        fig, axes = plt.subplots(1, len(ms), figsize=(5*len(ms), 4), squeeze=False)
        for j, m_val in enumerate(ms):
            data = sub[sub['m'] == m_val]
            box_data = [data[data['algorithm'] == a]['hv'].values for a in data['algorithm'].unique()]
            labels = data['algorithm'].unique()
            axes[0, j].boxplot(box_data, labels=labels)
            axes[0, j].set_title(f'{prob} m={m_val}')
            axes[0, j].set_ylabel('HV')
            axes[0, j].tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.show()

def plot_median_fronts(runs_store):
    """Plot median-HV Pareto fronts for each (problem, m).
    
    Uses scatter for m=2, and parallel coordinates for m>2.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from pandas.plotting import parallel_coordinates
    import pandas as pd
    for key, alg_dict in runs_store.items():
        problem, m = key
        all_runs = []
        for alg, runs in alg_dict.items():
            all_runs.extend(runs)
        if not all_runs:
            continue
        hvs = np.array([r.hv for r in all_runs])
        med_idx = np.argsort(hvs)[len(hvs) // 2]
        F = all_runs[med_idx].F
        if F.shape[1] == 2:
            plt.figure()
            plt.scatter(F[:, 0], F[:, 1], c='steelblue', alpha=0.7)
            plt.title(f'{problem} m={m}')
            plt.xlabel('$f_1$')
            plt.ylabel('$f_2$')
            plt.grid(True, alpha=0.3)
            plt.show()
        elif F.shape[1] >= 3:
            df = pd.DataFrame(F, columns=[f'$f_{{{i+1}}}$' for i in range(m)])
            df['solution'] = range(len(df))
            plt.figure(figsize=(10, 5))
            parallel_coordinates(df, class_column='solution', color='steelblue', alpha=0.3)
            plt.title(f'{problem} m={m} — Coordenadas paralelas (frente mediano HV)')
            plt.legend().remove()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

plt.rcParams['figure.dpi'] = 100
print('Plotting functions loaded.')\
'''))

# Benchmark execution
new.append(code('''\
PROBLEMS = ["dtlz1", "dtlz2", "dtlz7", "wfg1", "wfg3", "idtlz1", "idtlz2"]
MS = [2, 3, 5, 8, 10]
ALGORITHMS = ["nsga2", "rse-nsga2", "r-nsga2"]
N_RUNS = 30

print("Problemas:", PROBLEMS)
print("Dimensiones objetivo:", MS)
print("Algoritmos:", ALGORITHMS)
print("Corridas por configuracion:", N_RUNS)
print("Total ejecuciones:", len(PROBLEMS) * len(MS) * len(ALGORITHMS) * N_RUNS)\
'''))

new.append(code('''\
import time, traceback, os
start_ts = time.time()
print('Iniciando benchmark MOEA...')
try:
    df_runs, ref_points, runs_store = run_moea_benchmark(
        problems=PROBLEMS, objectives=MS, algorithms=ALGORITHMS,
        n_runs=N_RUNS, pop_size=100, n_gen=250, seed0=42
    )
except Exception:
    traceback.print_exc()
    raise
elapsed = time.time() - start_ts
print(f"\\nBenchmark completado en {elapsed/60:.1f} min.")
print(f"Total corridas: {len(df_runs)}")\
'''))

new.append(code('''\
# Tabla resumen por (problema, m, algoritmo)
summary = df_runs.groupby(['problem', 'm', 'algorithm'])['hv'].agg(['mean', 'std', 'count'])
summary = summary.round(4)
display(summary)\
'''))

new.append(code('''\
# Prueba de Wilcoxon: nsga2 vs r-nsga2, nsga2 vs r-nsga2-1k
from scipy.stats import wilcoxon
import pandas as pd

rows = []
for (prob, m), grp in df_runs.groupby(['problem', 'm']):
    for algo in ['r-nsga2', 'r-nsga2-1k']:
        a = grp[grp['algorithm'] == 'nsga2']['hv'].values
        b = grp[grp['algorithm'] == algo]['hv'].values
        if len(a) > 1 and len(b) > 1:
            try:
                stat, p = wilcoxon(a, b, alternative='two-sided')
                rows.append({'problem': prob, 'm': m, 'algo': algo, 'p_value': round(p, 6), 'significant': p < 0.05})
            except ValueError:
                rows.append({'problem': prob, 'm': m, 'algo': algo, 'p_value': None, 'significant': None})
wilcoxon_df = pd.DataFrame(rows)
display(wilcoxon_df)\
'''))

new.append(code('''\
print('Generando boxplots HV...')
plot_hv_boxplots(df_runs)
print('Generando frentes Pareto (mediana de HV)...')
plot_median_fronts(runs_store)
print('Todas las graficas generadas.')\
'''))

new.append(code('''\
import platform
def moea_platform_info():
    import pymoo
    return {
        'python': platform.python_version(),
        'numpy': __import__('numpy').__version__,
        'pandas': __import__('pandas').__version__,
        'matplotlib': __import__('matplotlib').__version__,
        'scipy': __import__('scipy').__version__,
        'pymoo': pymoo.__version__,
        'system': platform.platform(),
        'machine': platform.machine(),
        'cpu_count': str(os.cpu_count() or 1),
    }
print('\\nInformacion de plataforma:')
for k, v in moea_platform_info().items():
    print(f'  {k}: {v}')\
'''))

# ── Rebuild notebook ──
# Replace skeleton sections 1 and 2 with enhanced content + cone viz
skeleton = nb['cells'][:36]
skeleton[2] = new_section1
skeleton[3] = new_section2

# Remove any existing cone viz cells from prior runs in the skeleton
skeleton = [c for c in skeleton if not (c['cell_type'] == 'code' and 'Polygon' in ''.join(c.get('source', [])))]

# Insert the cone viz cell after section 2
skeleton.insert(4, cone_viz)

final_cells = skeleton + new + nb['cells'][-1:]
nb['cells'] = final_cells

with open('HW1_JR.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Notebook reconstruido. Total celdas: {len(final_cells)}")
print(f"Secciones MOEA reemplazadas con {len(new)} celdas nuevas.")
