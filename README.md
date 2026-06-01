# EMO-CICESE-Practices

Evolutionary Multi-Objective Optimization course assignments.  
**CICESE** — Student: Javier Ramirez Gonzalez — Instructor: Dr. Jesus Guillermo Falcon Cardona — 2026-2

---

## Setup

**Conda (recommended)**
```bash
conda env create -f environment.yml
conda activate emo-cicese
```

**pip**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Docker**
```bash
docker build -t emo-cicese . && docker run -p 8888:8888 emo-cicese
```

---

## Structure

```
├── HW1/                    Homework 1 — ND sorting & NSGA-II variants
├── Dockerfile              Container definition
├── environment.yml         Conda environment specification
├── requirements.txt        pip dependencies (pinned)
└── README.md
```

Additional homeworks will be added as the course progresses.

---

## Homework 1 — Non-Dominated Sorting & NSGA-II Variants

### Non-dominated sorting algorithms

Three algorithms to find the non-dominated set of N points in m dimensions, compiled with Numba JIT:

| Algorithm | Worst-case | Avg. (uniform) | Time (m=2, N=10K) |
|-----------|------------|----------------|-------------------|
| Naive     | O(mN^2)    | O(mN^2)        | 0.86 ms           |
| Bentley MTF | O(mN^2)  | O(N^{1+o(1)})  | 0.06 ms           |
| M3        | O(mN^2)    | O(N^{1+o(1)})  | 0.05 ms           |

Full pseudocode in [`nd_algorithms.py`](HW1/nd_algorithms.py).

### NSGA-II variants

Three algorithms benchmarked on DTLZ1/2/7, WFG1/3, IDTLZ1/2 (m = 2,3,5,8,10), 30 runs each, evaluated by Hypervolume (HV):

| Variant     | Modification |
|-------------|-------------|
| NSGA-II     | Baseline crowding distance |
| RSE-NSGA-II | Crowding distance replaced by Riesz s-Energy density (greedy subset selection) |
| R-NSGA-II   | Pareto dominance replaced by (1-K)-dominance (relaxation tolerating worse performance in up to k*m objectives) |

### Key results

| | m=2 | m=3 | m=10 |
|---|---|---|---|
| Time vs N | ![time m=2](HW1/resultados/graficas/tiempo_vs_N_m2.png) | ![time m=3](HW1/resultados/graficas/tiempo_vs_N_m3.png) | ![time m=10](HW1/resultados/graficas/tiempo_vs_N_m10.png) |
| Pareto front | ![front m=2](HW1/resultados/figuras/frente_N100_m2.png) | ![front m=3](HW1/resultados/figuras/frente_N100_m3.png) | ![front m=10](HW1/resultados/figuras/frente_N100_m10.png) |

| RSE subset selection | (1-K)-dominance |
|---|---|
| ![RSE](HW1/resultados/figuras/rse_demo.png) | ![(1-K)](HW1/resultados/figuras/one_k_dominance_demo.png) |

Full report: [`HW1/HW1_JR.ipynb`](HW1/HW1_JR.ipynb)

---

## Dependencies

| Package  | Version |
|----------|---------|
| Python   | 3.12.2  |
| numpy    | 2.3.5   |
| pandas   | 2.2.3   |
| scipy    | 1.15.3  |
| matplotlib | 3.10.7 |
| numba    | 0.62.1  |
| pymoo    | 0.6.1.6 |
| scikit-learn | 1.7.2 |

---

## License

MIT — (c) 2026 Javier Ramirez
