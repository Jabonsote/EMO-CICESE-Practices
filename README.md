# 🧬 EMO-CICESE-Practices

**Evolutionary Multi-Objective Optimization** · CICESE

| | |
|---|---|
| **Student** | Javier Ramírez González |
| **Instructor** | Dr. Jesús Guillermo Falcón Cardona |
| **Semester** | 2026-2 |

---

## 📋 Overview

Hands-on assignments for the *Evolutionary Multi-Objective Optimization* course. Implements non-dominated sorting algorithms, density estimators, relaxed dominance relations, and NSGA-II variants.

---

## 🚀 Quick Start

### Conda (recommended)

```bash
conda env create -f environment.yml
conda activate emo-cicese
```

### pip

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Docker (maximal reproducibility)

```bash
docker build -t emo-cicese .
docker run -p 8888:8888 emo-cicese
```

Open the Jupyter URL printed in the logs.

### Verify

```bash
python -c "
import numpy, pandas, scipy, matplotlib, numba, pymoo, sklearn
print('All dependencies OK')
"
```

---

## 📁 Structure

```
├── HW1/          # Homework 1 — ND sorting & NSGA-II variants
├── LICENSE
├── README.md
├── requirements.txt
├── environment.yml
└── Dockerfile
```

> More assignments will be added as the course progresses.

---

## 🧪 Homework 1 — Non-Dominated Sorting & NSGA-II Variants

### ND Sorting Algorithms

| Algorithm | Complexity | Performance (m=2, N=10K) |
|-----------|-----------|--------------------------|
| **Naive** | O(mN²) | ~0.86 ms |
| **Bentley MTF** | O(mN²) avg O(N^{1+o(1)}) | ~0.06 ms |
| **M3** | O(mN²) avg O(N^{1+o(1)}) | ~0.05 ms |

[Pseudocode](HW1/nd_algorithms.py) for all three.

### NSGA-II Variants

| Variant | Key Idea |
|---------|----------|
| **NSGA-II** | Baseline with crowding distance |
| **RSE-NSGA-II** | Replaces crowding distance with Riesz s-Energy density |
| **R-NSGA-II** | Uses (1-K)-dominance (tolerates worse in ≤ k·m objectives) |

Evaluated on DTLZ1/2/7, WFG1/3, IDTLZ1/2 with m∈{2,3,5,8,10}, 30 runs each, measured via Hypervolume (HV).

### Key Results

| | m=2 | m=3 | m=10 |
|:---:|:---:|:---:|:----:|
| **Time vs N** | ![time m=2](HW1/resultados/graficas/tiempo_vs_N_m2.png) | ![time m=3](HW1/resultados/graficas/tiempo_vs_N_m3.png) | ![time m=10](HW1/resultados/graficas/tiempo_vs_N_m10.png) |
| **Pareto front** | ![front m=2](HW1/resultados/figuras/frente_N100_m2.png) | ![front m=3](HW1/resultados/figuras/frente_N100_m3.png) | ![front m=10 PCA](HW1/resultados/figuras/frente_N100_m10.png) |

| RSE subset selection | (1-K)-Dominance |
|:-------------------:|:---------------:|
| ![RSE](HW1/resultados/figuras/rse_demo.png) | ![(1-K)](HW1/resultados/figuras/one_k_dominance_demo.png) |

Full report: [`HW1/HW1_JR.ipynb`](HW1/HW1_JR.ipynb)

---

## 🛠️ Tech Stack

| Tool | Version |
|------|---------|
| Python | 3.12.2 |
| NumPy | 2.3.5 |
| pandas | 2.2.3 |
| SciPy | 1.15.3 |
| Matplotlib | 3.10.7 |
| Numba | 0.62.1 |
| pymoo | 0.6.1.6 |
| scikit-learn | 1.7.2 |

---

## 📄 License

MIT — © 2026 Javier Ramírez
