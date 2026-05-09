from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import optuna
from bayes_opt import BayesianOptimization

from backend.core.services.observability_service import observability
from backend.core.tracing import trace_context


class HyperparameterOptimizer:
    """Unified interface supporting multiple HPO strategies."""

    @staticmethod
    async def run_comparison(
        objective_fn: Callable[[optuna.Trial], float],
        param_space: dict[str, tuple[float, float]],
        n_trials: int = 50,
        timeout: int = 1800,
    ) -> dict[str, Any]:
        """Run Optuna vs Bayesian Optimization and compare results."""
        with trace_context("hpo.comparison"):
            obs = observability()
            obs.increment("hpo_comparison_runs_total")

            results = {}

            # 1. Optuna (Tree-structured Parzen Estimator)
            start = time.time()
            study = optuna.create_study(direction="minimize")
            study.optimize(objective_fn, n_trials=n_trials, timeout=timeout)
            optuna_time = time.time() - start

            results["optuna"] = {
                "best_value": study.best_value,
                "best_params": study.best_params,
                "time_seconds": optuna_time,
                "n_trials": len(study.trials),
            }

            # 2. Bayesian Optimization (bayes_opt)
            start = time.time()

            # Helper to adapt Optuna's objective_fn for Bayesian Optimization
            def bo_objective(**p: float) -> float:
                # Mock a trial for bayesian optimization parameters
                trial = optuna.trial.FixedTrial(p)
                return -objective_fn(trial)

            optimizer = BayesianOptimization(
                f=bo_objective,
                pbounds={k: v for k, v in param_space.items()},
                random_state=42,
                verbose=0,
            )
            optimizer.maximize(init_points=5, n_iter=n_trials - 5)
            bo_time = time.time() - start

            results["bayesian_opt"] = {
                "best_value": -optimizer.max["target"],
                "best_params": optimizer.max["params"],
                "time_seconds": bo_time,
                "n_trials": n_trials,
            }

            # Summary comparison
            comparison = {
                "winner": "optuna"
                if results["optuna"]["best_value"] < results["bayesian_opt"]["best_value"]
                else "bayesian_opt",
                "optuna": results["optuna"],
                "bayesian_opt": results["bayesian_opt"],
                "speedup": results["bayesian_opt"]["time_seconds"] / results["optuna"]["time_seconds"],
            }

            obs.gauge(
                "hpo_best_loss",
                min(results["optuna"]["best_value"], results["bayesian_opt"]["best_value"]),
            )
            return comparison
