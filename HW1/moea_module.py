"""
moea_module.py — MOEA components for Tarea 1 EMO.
RSE density, (1-K)-dominance, NSGA-II variants, benchmark utilities.
"""
import numpy as np
import time
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed


# ── Riesz s-energy (RSE) ──

def riesz_energy_matrix(F, s):
    """Riesz s-energy matrix between point pairs (uses pdist for speed)."""
    from scipy.spatial.distance import pdist, squareform
    F = np.asarray(F, dtype=float)
    dist = squareform(pdist(F))
    K = np.zeros_like(dist)
    mask = dist > 1e-15
    K[mask] = 1.0 / np.power(dist[mask], s)
    np.fill_diagonal(K, 0.0)
    return K


def normalize_objectives(F):
    """Normalize objectives to [0,1] range."""
    F = np.asarray(F, dtype=float)
    lo, hi = F.min(axis=0), F.max(axis=0)
    denom = hi - lo
    denom[denom == 0.0] = 1.0
    return (F - lo) / denom


def greedy_rse_removal(F, n_survive, s=None):
    """Greedy RSE subset selection by removal (Falcon-Cardona et al.).
    
    Uses boolean mask instead of np.delete to avoid O(N^3) copies.
    """
    F = np.asarray(F, dtype=float)
    n, m = F.shape
    if n <= n_survive:
        return np.arange(n, dtype=int)
    if s is None:
        s = float(m - 1)
    Fn = normalize_objectives(F)
    K = riesz_energy_matrix(Fn, s)
    contrib = np.sum(K, axis=1)
    alive = np.ones(n, dtype=bool)
    n_alive = n
    while n_alive > n_survive:
        idx_alive = np.where(alive)[0]
        worst = idx_alive[np.argmax(contrib[idx_alive])]
        alive[worst] = False
        n_alive -= 1
        contrib -= K[:, worst]
    return np.where(alive)[0]


# ── (1-K)-Dominance ──

def dominates_one_minus_k(a, b, k=0.25, atol=1e-12):
    """Check if a (1-k)-dominates b (Farina & Amato 2004)."""
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    m = len(a)
    leq = int(np.sum(a <= b + atol))
    lt = int(np.sum(a < b - atol))
    k_int = int(np.floor(k * m)) if isinstance(k, float) and k < 1 else int(k)
    return leq >= (m - k_int) and lt >= 1


def dominates_pareto(a, b):
    """Standard Pareto dominance."""
    return np.all(a <= b) and np.any(a < b)


def fast_non_dominated_sort(F, dominates_fn):
    """Generic fast non-dominated sort O(mN²). Returns list of fronts."""
    F = np.atleast_2d(np.asarray(F, dtype=float))
    n = F.shape[0]
    if n == 0:
        return []
    S = [set() for _ in range(n)]
    n_dom = np.zeros(n, dtype=int)
    for p in range(n):
        for q in range(p + 1, n):
            if dominates_fn(F[p], F[q]):
                S[p].add(q)
                n_dom[q] += 1
            elif dominates_fn(F[q], F[p]):
                S[q].add(p)
                n_dom[p] += 1
    first_front = [i for i in range(n) if n_dom[i] == 0]
    fronts = []
    current = first_front
    while current:
        fronts.append(np.array(current, dtype=int))
        next_front = []
        for p in current:
            for q in S[p]:
                n_dom[q] -= 1
                if n_dom[q] == 0:
                    next_front.append(q)
        current = next_front
    return fronts


def crowding_distance(F):
    """Standard crowding distance."""
    F = np.atleast_2d(np.asarray(F, dtype=float))
    n, m = F.shape
    if n <= 2:
        return np.full(n, np.inf)
    cd = np.zeros(n, dtype=float)
    span = np.ptp(F, axis=0)
    span[span == 0.0] = 1.0
    for j in range(m):
        order = np.argsort(F[:, j], kind='mergesort')
        cd[order[0]] = np.inf
        cd[order[-1]] = np.inf
        cd[order[1:-1]] += (F[order[2:], j] - F[order[:-2], j]) / span[j]
    return cd


# ── NSGA-II Variants (pymoo) ──
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.survival import Survival
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting


class RSESurvival(Survival):
    """Survival replacing crowding distance with RSE."""
    def __init__(self, s=None):
        super().__init__(filter_infeasible=True)
        self.s = s

    def _do(self, problem, pop, n_survive, **kwargs):
        F = np.asarray(pop.get('F'), dtype=float)
        fronts = NonDominatedSorting().do(F)
        for k, front in enumerate(fronts):
            for j, i in enumerate(front):
                pop[i].set('rank', k)
                pop[i].set('crowding', -j)
        survivors = []
        for front in fronts:
            if len(survivors) + len(front) <= n_survive:
                for i in front:
                    survivors.append(i)
            else:
                remain = n_survive - len(survivors)
                chosen = greedy_rse_removal(F[front], remain, self.s)
                for idx in chosen:
                    survivors.append(front[idx])
                break
        out = pop[survivors]
        F2 = np.asarray(out.get('F'), dtype=float)
        f2s = NonDominatedSorting().do(F2)
        for k, f2 in enumerate(f2s):
            for j, i in enumerate(f2):
                out[i].set('rank', k)
        cd = crowding_distance(F2)
        cd[np.isnan(cd)] = np.inf
        for i in range(len(out)):
            out[i].set('crowding', cd[i])
        return out


class RelationSurvival(Survival):
    """Survival based on (1-K)-dominance."""
    def __init__(self, k=0.25):
        super().__init__(filter_infeasible=True)
        self.k = k

    def _do(self, problem, pop, n_survive, **kwargs):
        F = np.asarray(pop.get('F'), dtype=float)
        dom_k = lambda a, b: dominates_one_minus_k(a, b, self.k)
        fronts = fast_non_dominated_sort(F, dom_k)
        for kk, front in enumerate(fronts):
            for j, i in enumerate(front):
                pop[i].set('rank', kk)
                pop[i].set('crowding', -j)
        survivors = []
        all_indices = np.arange(len(F))
        used = np.zeros(len(F), dtype=bool)
        for front in fronts:
            if len(survivors) + len(front) <= n_survive:
                for i in front:
                    survivors.append(i)
                    used[i] = True
            else:
                remain = n_survive - len(survivors)
                cd = crowding_distance(F[front])
                order = np.argsort(-cd, kind='mergesort')
                for idx in order[:remain]:
                    survivors.append(front[idx])
                    used[front[idx]] = True
                break
        if len(survivors) < n_survive:
            extra = all_indices[~used]
            n_need = n_survive - len(survivors)
            for i in extra[:n_need]:
                survivors.append(i)
        out = pop[survivors]
        out.set('rank', 0)
        F2 = np.asarray(out.get('F'), dtype=float)
        if len(F2) > 0:
            cd = crowding_distance(F2)
            cd[np.isnan(cd)] = np.inf
            for i in range(len(out)):
                out[i].set('crowding', cd[i])
        return out


class RSENSGA2(NSGA2):
    """NSGA-II with RSE density estimator."""
    def __init__(self, pop_size=100, s=None, **kwargs):
        super().__init__(pop_size=pop_size, survival=RSESurvival(s=s), **kwargs)


class RelNSGA2(NSGA2):
    """NSGA-II with (1-K)-dominance based ranking."""
    def __init__(self, pop_size=100, k=0.25, **kwargs):
        super().__init__(pop_size=pop_size, survival=RelationSurvival(k=k), **kwargs)


# ── IDTLZ problems ──
from pymoo.core.problem import Problem


class IDTLZ1(Problem):
    """Inverted DTLZ1."""
    def __init__(self, n_var, n_obj, **kwargs):
        super().__init__(n_var=n_var, n_obj=n_obj, xl=0.0, xu=1.0, **kwargs)
        self.k = n_var - n_obj + 1

    def _evaluate(self, x, out, *args, **kwargs):
        x = np.asarray(x, dtype=float)
        X_ = x[:, :self.n_obj - 1]
        X_M = x[:, self.n_obj - 1:]
        g = 100.0 * (self.k + np.sum((X_M - 0.5)**2 -
                     np.cos(20.0 * np.pi * (X_M - 0.5)), axis=1))
        base = []
        for i in range(self.n_obj):
            f = 0.5 * (1.0 + g)
            if self.n_obj - 1 - i > 0:
                f *= np.prod(X_[:, :self.n_obj - 1 - i], axis=1)
            if i > 0:
                f *= (1.0 - X_[:, self.n_obj - 1 - i])
            base.append(f)
        base = np.column_stack(base)
        out['F'] = 0.5 * (1.0 + g[:, None]) - base


class IDTLZ2(Problem):
    """Inverted DTLZ2."""
    def __init__(self, n_var, n_obj, **kwargs):
        super().__init__(n_var=n_var, n_obj=n_obj, xl=0.0, xu=1.0, **kwargs)
        self.k = n_var - n_obj + 1

    def _evaluate(self, x, out, *args, **kwargs):
        x = np.asarray(x, dtype=float)
        X_ = x[:, :self.n_obj - 1]
        X_M = x[:, self.n_obj - 1:]
        g = np.sum((X_M - 0.5)**2, axis=1)
        base = []
        for i in range(self.n_obj):
            f = 1.0 + g
            if self.n_obj - 1 - i > 0:
                f *= np.prod(np.cos(X_[:, :self.n_obj - 1 - i] * np.pi / 2.0), axis=1)
            if i > 0:
                f *= np.sin(X_[:, self.n_obj - 1 - i] * np.pi / 2.0)
            base.append(f)
        base = np.column_stack(base)
        out['F'] = 1.0 + g[:, None] - base


# ── MOEA Benchmark Utilities ──
from pymoo.optimize import minimize
from pymoo.indicators.hv import HV
from pymoo.problems import get_problem


def standard_n_var(problem_name, m):
    """Standard number of decision variables."""
    name = problem_name.lower()
    if name in {'dtlz1', 'idtlz1'}:
        return m + 4
    if name in {'dtlz2', 'dtlz3', 'dtlz4', 'dtlz5', 'dtlz6', 'idtlz2'}:
        return m + 9
    if name == 'dtlz7':
        return m + 19
    if name in {'wfg1', 'wfg3'}:
        return 2 * (m - 1) + 20
    raise ValueError(f'Unsupported problem: {problem_name}')


def make_problem(problem_name, m):
    """Create problem instance."""
    name = problem_name.lower()
    n_var = standard_n_var(name, m)
    if name in {'dtlz1', 'dtlz2', 'dtlz3', 'dtlz4', 'dtlz5', 'dtlz6', 'dtlz7', 'wfg1', 'wfg3'}:
        return get_problem(name, n_var=n_var, n_obj=m)
    if name == 'idtlz1':
        return IDTLZ1(n_var=n_var, n_obj=m)
    if name == 'idtlz2':
        return IDTLZ2(n_var=n_var, n_obj=m)
    raise ValueError(f'Unrecognized problem: {problem_name}')


def build_reference_point(problem_name, problem, m, seed=123):
    """Conservative reference point for HV."""
    name = problem_name.lower()
    rng = np.random.default_rng(seed)
    X = rng.random((2000, problem.n_var))
    F = np.asarray(problem.evaluate(X, return_values_of=['F']), dtype=float)
    max_f = np.max(F, axis=0)
    spread = np.maximum(np.ptp(F, axis=0), 1e-12)
    ref = max_f + 0.1 * spread + 1e-6
    if name in {'dtlz1', 'idtlz1'}:
        ref = np.maximum(ref, np.full(m, 1.0))
    elif name in {'dtlz2', 'idtlz2'}:
        ref = np.maximum(ref, np.full(m, 1.2))
    elif name == 'dtlz7':
        ref = np.maximum(ref[:m - 1], np.full(m - 1, 1.2))
        ref = np.concatenate([ref, np.array([2.0 * m + 1.0])])
    elif name in {'wfg1', 'wfg3'}:
        ref = max_f + 0.25 * np.abs(max_f) + 1.0
    return ref.astype(float)


def make_algorithm(algorithm_name, m, pop_size=100):
    """Create NSGA-II or variant."""
    name = algorithm_name.lower()
    if name == 'nsga2':
        return NSGA2(pop_size=pop_size)
    if name == 'rse-nsga2':
        return RSENSGA2(pop_size=pop_size, s=float(m - 1))
    if name == 'r-nsga2':
        return RelNSGA2(pop_size=pop_size, k=0.25)
    raise ValueError(f'Unrecognized algorithm: {algorithm_name}')


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
    return _problem_cache[key]

def _moea_worker(args):
    """Single optimization (for parallel executor).
    
    Does NOT compute HV inside the worker — returns F.
    HV is computed later (offline) to avoid bottlenecking parallel workers.
    """
    import traceback
    try:
        problem_name, m, algorithm_name, seed, pop_size, n_gen = args
        problem = _get_problem_cached(problem_name, m)
        algorithm = make_algorithm(algorithm_name, m=m, pop_size=pop_size)
        t0 = time.perf_counter()
        res = minimize(problem, algorithm, ('n_gen', n_gen), seed=seed, verbose=False)
        exec_ms = (time.perf_counter() - t0) * 1000.0
        F = np.asarray(res.F, dtype=float)
        return RunResult(problem=problem_name, m=m, algorithm=algorithm_name,
                         seed=seed, hv=0.0, F=F,
                         exec_time_ms=exec_ms, hv_time_ms=0.0)
    except Exception:
        print("\n" + "=" * 80)
        print("WORKER CRASH")
        print(args)
        print("=" * 80)
        traceback.print_exc()
        raise


def run_moea_benchmark(problems, objectives, algorithms,
                       pop_size=100, n_gen=250, n_runs=30,
                       n_jobs=None, seed0=2026, verbose=True,
                       cache_ref=True):
    """Run full MOEA benchmark in parallel.
    
    Parameters
    ----------
    cache_ref : bool
        Cache reference points to disk to avoid recomputation.
    """
    import pandas as pd, os, pickle, traceback
    CACHE_FILE = 'ref_points_cache.pkl'
    if n_jobs is None:
        n_jobs = max(1, (os.cpu_count() or 1) - 1)

    if verbose:
        print("Computing reference points...")
    ref_points = {}
    if cache_ref:
        try:
            with open(CACHE_FILE, 'rb') as f:
                cached = pickle.load(f)
            for (p, m), rp in cached.items():
                if p in problems and m in objectives:
                    ref_points[(p, m)] = rp
            if ref_points:
                if verbose:
                    print(f"  Loaded {len(ref_points)} from cache ({CACHE_FILE})")
        except (FileNotFoundError, pickle.UnpicklingError, EOFError, KeyError):
            ref_points = {}
    missing = [(p, m) for p in problems for m in objectives if (p, m) not in ref_points]
    for p, m in missing:
        prob = make_problem(p, m)
        ref_points[(p, m)] = build_reference_point(p, prob, m, seed=seed0 + 999)
    if cache_ref and missing:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(ref_points, f)
        if verbose:
            print(f"  Cached {len(ref_points)} reference points ({CACHE_FILE})")

    runs_store = {(p, m): {alg: [] for alg in algorithms}
                  for p in problems for m in objectives}

    jobs = []
    for p_idx, pn in enumerate(problems):
        for m_idx, m in enumerate(objectives):
            for a_idx, alg in enumerate(algorithms):
                for r in range(n_runs):
                    seed = seed0 + 100000 * p_idx + 1000 * m_idx + 100 * a_idx + r
                    jobs.append((pn, m, alg, seed, pop_size, n_gen))

    n_total = len(jobs)
    if verbose:
        print(f"\nMOEA benchmark: {n_total} runs")
        print(f"  Problems: {list(problems)} | m: {list(objectives)} | Algorithms: {list(algorithms)}")
        print(f"  Runs/config: {n_runs} | Cores: {n_jobs}")
        print("-" * 60)

    algo_done = {alg: 0 for alg in algorithms}
    df_rows = []
    done = 0
    t0_progress = time.time()
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        fut_map = {executor.submit(_moea_worker, j): j for j in jobs}
        for fut in as_completed(fut_map):
            try:
                res = fut.result()
                df_rows.append({
                    'problem': res.problem, 'm': res.m,
                    'algorithm': res.algorithm, 'seed': res.seed,
                    'hv': 0.0, 'exec_time_ms': res.exec_time_ms,
                    'hv_time_ms': 0.0,
                })
                runs_store[(res.problem, res.m)][res.algorithm].append(res)
                algo_done[res.algorithm] += 1
            except Exception:
                print(f"\n[ERR] Job: {fut_map[fut]}")
                traceback.print_exc()
            done += 1
            report_every = max(1, min(50, n_total // 100))
            if verbose and (done % report_every == 0 or done == n_total):
                elapsed = time.time() - t0_progress
                rate = done / elapsed if elapsed > 0 else 0
                eta_min = (n_total - done) / rate / 60 if rate > 0 else 0
                algo_str = ' | '.join(f'{a}={algo_done[a]}' for a in algorithms)
                print(f"  [{done}/{n_total} {done/n_total*100:.0f}%] "
                      f"{elapsed/60:.1f}min ETA {eta_min:.0f}min | {algo_str}")

    df = pd.DataFrame(df_rows)
    if verbose:
        print(f"  Completed: {len(df)} runs\n")

    # ── Compute HV offline ──
    if verbose:
        print("Computing Hypervolume (offline)...")
    hv_ind_cache = {}
    for i, (_, row) in enumerate(df.iterrows()):
        key = (row['problem'], row['m'])
        if key not in hv_ind_cache:
            hv_ind_cache[key] = HV(ref_point=ref_points[key])
        res_list = runs_store[(row['problem'], row['m'])][row['algorithm']]
        idx_in_store = row['seed'] - seed0  # approximate offset
        # find matching RunResult by seed
        for rr in res_list:
            if rr.seed == row['seed']:
                t0 = time.perf_counter()
                df.at[i, 'hv'] = float(hv_ind_cache[key](rr.F))
                df.at[i, 'hv_time_ms'] = (time.perf_counter() - t0) * 1000.0
                break
    if verbose:
        print(f"  HV computed for all {len(df)} runs\n")

    return df, ref_points, runs_store
