import numpy as np
import pandas as pd
import time

from concurrent.futures import ProcessPoolExecutor
from numba import njit


# =====================================================
# NUMBA DOMINANCE
# =====================================================

@njit(cache=True, fastmath=True)
def dominates(p, q):

    better = False

    for k in range(p.shape[0]):

        if p[k] > q[k]:
            return False

        if p[k] < q[k]:
            better = True

    return better


# =====================================================
# NAIVE
# =====================================================

@njit(cache=True, fastmath=True)
def naive_nondominated(A):

    N = A.shape[0]

    dominated = np.zeros(
        N,
        dtype=np.uint8
    )

    for i in range(N):

        if dominated[i]:
            continue

        for j in range(N):

            if i == j:
                continue

            if dominates(A[j], A[i]):

                dominated[i] = 1
                break

    count = 0

    for i in range(N):
        if dominated[i] == 0:
            count += 1

    result = np.empty(
        count,
        dtype=np.int32
    )

    pos = 0

    for i in range(N):

        if dominated[i] == 0:

            result[pos] = i
            pos += 1

    return result


# =====================================================
# MTF
# =====================================================

@njit(cache=True, fastmath=True)
def sequential_mtf_nondominated(A):

    N = A.shape[0]

    active = np.empty(
        N,
        dtype=np.int32
    )

    size = 0

    for i in range(N):

        dominated_flag = False

        j = 0

        while j < size:

            idx = active[j]

            if dominates(A[idx], A[i]):

                dominated_flag = True

                if j > 0:

                    tmp = active[j]

                    active[1:j+1] = active[0:j]

                    active[0] = tmp

                break

            elif dominates(A[i], A[idx]):

                active[j] = active[size-1]
                size -= 1

            else:

                j += 1

        if not dominated_flag:

            active[size] = i
            size += 1

    return active[:size].copy()


# =====================================================
# M3
# =====================================================

@njit(cache=True, fastmath=True)
def m3_nondominated(A):

    N = A.shape[0]

    active = np.empty(
        N,
        dtype=np.int32
    )

    active[0] = 0

    top = 0

    for i in range(1, N):

        j = 0

        dominated_flag = False

        while j <= top:

            idx = active[j]

            if dominates(A[idx], A[i]):

                tmp = active[0]
                active[0] = active[j]
                active[j] = tmp

                dominated_flag = True
                break

            elif dominates(A[i], A[idx]):

                tmp = active[j]
                active[j] = active[top]
                active[top] = tmp

                top -= 1

            else:

                j += 1

        if not dominated_flag:

            top += 1
            active[top] = i

    return active[:top+1].copy()


# =====================================================
# DATASET GENERATION
# =====================================================

def generate_uniform_points(
    N,
    m,
    seed
):

    rng = np.random.default_rng(seed)

    return rng.random(
        (N, m),
        dtype=np.float32
    )


# =====================================================
# BENCHMARK WORKER
# =====================================================

def benchmark_one(config):

    N, m, trial, A = config

    results = {}

    algs = [
        ("Naive", naive_nondominated),
        ("MTF", sequential_mtf_nondominated),
        ("M3", m3_nondominated),
    ]

    reference = None

    for name, alg in algs:

        t0 = time.perf_counter()

        idx = alg(A)

        elapsed = (
            time.perf_counter() - t0
        ) * 1000

        results[name] = elapsed

        current = set(idx.tolist())

        if reference is None:

            reference = current

        else:

            assert current == reference

    return {
        "N": N,
        "m": m,
        "trial": trial,
        "nd_size": len(reference),
        "Naive_ms": results["Naive"],
        "MTF_ms": results["MTF"],
        "M3_ms": results["M3"]
    }


# =====================================================
# PARALLEL BENCHMARK
# =====================================================

def run_nd_benchmark(
    N_values=(10,100,1000,10000),
    m_values=(2,3,10),
    trials=30,
    seed0=2026,
    workers=8
):

    # Pre-generate all datasets once
    datasets = {}

    for m in m_values:
        for N in N_values:
            for trial in range(trials):
                seed = seed0 + m*100000 + N*100 + trial
                datasets[(m, N, trial)] = generate_uniform_points(N, m, seed)

    configs = []

    for m in m_values:
        for N in N_values:
            for trial in range(trials):
                configs.append((N, m, trial, datasets[(m, N, trial)]))

    with ProcessPoolExecutor(
        max_workers=workers
    ) as pool:

        results = list(
            pool.map(
                benchmark_one,
                configs,
                chunksize=4
            )
        )

    return pd.DataFrame(results)