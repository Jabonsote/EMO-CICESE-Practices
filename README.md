
# 🧬 EMO-CICESE-Practices

**Optimización Evolutiva Multiobjetivo**  
**CICESE** — Centro de Investigación Científica y de Educación Superior de Ensenada

| | |
|---|---|
| **Estudiante** | Javier Ramírez González ([javier.ramirez@cicese.edu.mx](mailto:javier.ramirez@cicese.edu.mx)) |
| **Instructor** | Dr. Jesús Guillermo Falcón Cardona |
| **Semestre** | 2026-2 |

---

## 📋 Descripción

Repositorio de prácticas de la materia *Optimización Evolutiva Multiobjetivo*. Contiene implementaciones, experimentos y reportes sobre algoritmos de ordenamiento no dominado, estimadores de densidad, relaciones de dominancia relajada y variantes de NSGA-II.

> ⏳ *Se irán agregando más prácticas conforme avance el curso.*

---

## 📂 Estructura

```
EMO-CICESE-Practices/
├── HW1/                          # Tarea 1 — Algoritmos de ordenamiento no dominado y variantes de NSGA-II
│   ├── EMO_HW1.pdf               # Reporte en PDF (LaTeX)
│   ├── HW1_JR.ipynb              # Jupyter Notebook con el reporte completo
│   ├── HW1_JR.pdf                # Reporte exportado desde el notebook
│   ├── nd_algorithms.py          # Algoritmos de ordenamiento no dominado (Naive, Bentley MTF, M3)
│   ├── moea_module.py            # Componentes MOEA: RSE, (1-K)-dominancia, variantes NSGA-II
│   ├── gen_moea.py               # Script de generación de celdas para el notebook
│   ├── HW1_JR_images/            # 54 figuras embebidas en el notebook
│   └── resultados/
│       ├── csv/                  # Resultados numéricos (promedio y detallados)
│       ├── figuras/              # Frentes de Pareto 2D/3D/10D y demos
│       └── graficas/             # Gráficas tiempo vs N
├── LICENSE                       # MIT License
└── README.md
```

---

## 🧪 Tarea 1 — Algoritmos de Ordenamiento No Dominado

### Algoritmos Implementados

Tres algoritmos para encontrar el **conjunto no dominado** en un conjunto de `N` puntos en `m` dimensiones:

| Algoritmo | Peor caso | Caso promedio (uniforme) |
|-----------|-----------|--------------------------|
| **Naive** | O(mN²)    | O(mN²) |
| **Bentley MTF** | O(mN²) | O(N^{1+o(1)} + mN) |
| **M3** | O(mN²) | O(N^{1+o(1)} + mN) |

#### Naive

```
1:  dominated ← arreglo booleano de tamaño N (inicializado en Falso)
2:  para cada i en {0..N-1}:
3:      para cada j en {0..N-1} con j ≠ i:
4:          si A[j] domina a A[i]:
5:              dominated[i] ← Verdadero
6:              break
7:  retornar índices donde dominated es Falso
```

#### Bentley con Move-To-Front (MTF)

```
1:  active ← lista vacía
2:  para cada punto p en A:
3:      dominado ← Falso
4:      para cada candidato q en active:
5:          si q domina a p:
6:              mover q al frente de active  (MTF)
7:              dominado ← Verdadero
8:              break
9:          si p domina a q:
10:             eliminar q de active
11:     si no dominado:
12:         agregar p al final de active
13: retornar active
```

#### M3

```
1:  active[0] ← 0, top ← 0
2:  para cada punto p en A[1..N-1]:
3:      j ← 0, dominado ← Falso
4:      mientras j ≤ top:
5:          q ← active[j]
6:          si q domina a p:
7:             intercambiar active[0] ↔ active[j]
8:             dominado ← Verdadero
9:             break
10:         si p domina a q:
11:             intercambiar active[j] ↔ active[top]
12:             top ← top - 1
13:         si no:
14:             j ← j + 1
15:     si no dominado:
16:         top ← top + 1
17:         active[top] ← i
18: retornar active[0..top]
```

---

### 🧪 Variantes de NSGA-II

Tres algoritmos evaluados en 7 problemas benchmark (DTLZ1, DTLZ2, DTLZ7, WFG1, WFG3, IDTLZ1, IDTLZ2) con `m ∈ {2,3,5,8,10}`, 30 ejecuciones cada uno, usando **Hipervolumen (HV)** como métrica de calidad:

| Algoritmo | Descripción |
|-----------|-------------|
| **NSGA-II** | Algoritmo clásico con crowding distance (línea base) |
| **RSE-NSGA-II** | Reemplaza crowding distance por **Riesz s-Energy** como estimador de densidad (selección greedy por eliminación) |
| **R-NSGA-II** | Reemplaza dominancia de Pareto por **(1-K)-dominancia** (relajación que tolera estar peor en hasta `k·m` objetivos) |

#### RSE (Riesz s-Energy)

```
1: Normalizar objetivos F → [0,1]
2: Calcular matriz de energía Riesz: K_ij = 1 / ‖f_i - f_j‖^s
3: contrib ← suma por filas de K
4: Mientras n_alive > n_survive:
5:     idx = argmax(contrib)      # punto con mayor contribución
6:     eliminar idx del conjunto
7:     contrib ← contrib - K[:, idx]
8: Retornar índices sobrevivientes
```

#### (1-K)-Dominancia

```
Dados a, b ∈ ℝ^m y k ∈ [0,1]:
    a (1-k)-domina a b si:
        |{i : a_i ≤ b_i}| ≥ m - ⌊k·m⌋   (mejor o igual en al menos m-k·m objetivos)
        y |{i : a_i < b_i}| ≥ 1          (estrictamente mejor en al menos uno)
```

---

## 📊 Gráficas Representativas

### Tiempo de ejecución vs N (algoritmos de ordenamiento)

<p float="left">
  <img src="HW1/resultados/graficas/tiempo_vs_N_m2.png" width="30%" />
  <img src="HW1/resultados/graficas/tiempo_vs_N_m3.png" width="30%" />
  <img src="HW1/resultados/graficas/tiempo_vs_N_m10.png" width="30%" />
</p>

*Tiempo de ejecución (escala lineal y log-log) para m = 2, 3, 10 variando N de 10 a 10000. M3 y MTF son ~17× más rápidos que Naive en m=2 con N=10000.*

### Frentes de Pareto (DTLZ2)

<p float="left">
  <img src="HW1/resultados/figuras/frente_N100_m2.png" width="30%" />
  <img src="HW1/resultados/figuras/frente_N100_m3.png" width="30%" />
  <img src="HW1/resultados/figuras/frente_N100_m10.png" width="30%" />
</p>

*Frentes de Pareto obtenidos con NSGA-II para m = 2, 3, 10 (proyección PCA para m=10) con N=100.*

### Demostración de RSE

<p float="left">
  <img src="HW1/resultados/figuras/rse_demo.png" width="45%" />
  <img src="HW1/resultados/figuras/one_k_dominance_demo.png" width="45%" />
</p>

*Izquierda: Selección de 10 puntos de 50 usando RSE. Derecha: (1-K)-dominancia con k = 0, 0.25, 0.5.*

---

## 🛠️ Tecnologías

| Herramienta | Propósito |
|-------------|-----------|
| Python 3.12 | Lenguaje principal |
| NumPy | Computación numérica |
| Numba | Compilación JIT (algoritmos ND) |
| pymoo | Framework MOEA (NSGA-II, problemas benchmark) |
| SciPy | RSE (pdist), PCA |
| Matplotlib | Visualización |
| Jupyter | Reporte interactivo |

---

## 📄 Licencia

MIT License — Copyright © 2026 Javier Ramírez González
