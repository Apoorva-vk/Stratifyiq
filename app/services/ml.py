"""Prediction engine.

Three random-forest regressors predict delay risk, success probability and budget
overrun from project features. They are trained at first use on a synthetic dataset
whose labels follow documented business rules plus noise. The synthetic training is
an explicit limitation to state in the report; the same interface accepts real
historical project data later.
"""
from functools import lru_cache

import numpy as np
from sklearn.ensemble import RandomForestRegressor

FEATURES = ["budget_used_ratio", "progress", "load_ratio", "days_left", "team_size", "scope_units"]
BOUNDS = {"delay_risk": (0.0, 1.0), "success_probability": (0.0, 100.0), "overrun_pct": (-50.0, 150.0)}


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))


def _synthetic_dataset(n: int = 3000, seed: int = 42):
    rng = np.random.default_rng(seed)
    used = rng.uniform(0, 1.6, n)            # budget used ratio
    progress = rng.uniform(0, 100, n)
    load = rng.uniform(0.2, 2.5, n)          # workload vs capacity
    days = rng.uniform(0, 180, n)
    team = rng.integers(1, 15, n).astype(float)
    scope = rng.uniform(20, 300, n)
    X = np.column_stack([used, progress, load, days, team, scope])

    gap = used - progress / 100              # spending ahead of progress
    delay = _sigmoid(2.5 * (load - 1) + 1.5 * gap - 0.02 * (days - 45) + rng.normal(0, 0.25, n))
    success = np.clip((1 - delay) * 100 + rng.normal(0, 5, n), 0, 100)
    overrun = np.clip(gap * 100 + 15 * (load - 1) + rng.normal(0, 5, n), -50, 150)
    return X, delay, success, overrun


@lru_cache(maxsize=1)
def get_models() -> dict:
    X, y_delay, y_success, y_overrun = _synthetic_dataset()
    targets = {"delay_risk": y_delay, "success_probability": y_success, "overrun_pct": y_overrun}
    return {
        name: RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42).fit(X, y)
        for name, y in targets.items()
    }


def risk_level(delay_risk: float) -> str:
    if delay_risk < 0.35:
        return "LOW"
    if delay_risk < 0.65:
        return "MEDIUM"
    return "HIGH"


def predict(features: dict) -> dict:
    models = get_models()
    x = np.array([[features[f] for f in FEATURES]])
    out = {}
    for name, model in models.items():
        lo, hi = BOUNDS[name]
        out[name] = round(float(np.clip(model.predict(x)[0], lo, hi)), 3)
    out["resource_utilization_pct"] = round(features["load_ratio"] * 100, 1)
    out["risk_level"] = risk_level(out["delay_risk"])
    return out
