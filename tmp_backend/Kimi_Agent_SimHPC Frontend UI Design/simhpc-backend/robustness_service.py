"""
Robustness Orchestrator Service

This module provides parameter variation generation, simulation batching,
result aggregation, and statistical analysis for MFEM + SUNDIALS simulations.

Design Principle: Physics engines remain deterministic. AI layer remains advisory.
"""

import numpy as np
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SamplingMethod(Enum):
    """Supported parameter perturbation methods."""
    PERCENTAGE_5 = "±5%"
    PERCENTAGE_10 = "±10%"
    LATIN_HYPERCUBE = "latin_hypercube"


@dataclass
class ParameterConfig:
    """Configuration for a single parameter."""
    name: str
    base_value: float
    unit: str = ""
    description: str = ""
    perturbable: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class RobustnessConfig:
    """Configuration for robustness analysis."""
    enabled: bool = False
    num_runs: int = 15
    sampling_method: SamplingMethod = SamplingMethod.PERCENTAGE_10
    parameters: List[ParameterConfig] = field(default_factory=list)
    convergence_timeout_sec: float = 300.0
    random_seed: Optional[int] = None


@dataclass
class SimulationResult:
    """Result from a single simulation run."""
    run_id: int
    parameters: Dict[str, float]
    convergence_time_sec: float
    max_temperature: float
    min_temperature: float
    peak_stress: float
    residual_tolerance: float
    converged: bool
    failure_reason: Optional[str] = None
    mesh_elements: int = 0
    timestep_count: int = 0


@dataclass
class SensitivityMetric:
    """Sensitivity metric for a single parameter."""
    parameter_name: str
    influence_coefficient: float
    variance_contribution: float
    rank: int = 0


@dataclass
class RobustnessSummary:
    """Aggregated robustness analysis results."""
    baseline_result: SimulationResult
    all_results: List[SimulationResult]
    sensitivity_ranking: List[SensitivityMetric]
    confidence_interval_percent: float
    variance: float
    standard_deviation: float
    non_convergent_count: int
    run_count: int
    sampling_method: str
    computation_time_sec: float


@dataclass
class AIReportInput:
    """Structured input for AI report generation."""
    solver: str = "MFEM + SUNDIALS"
    mesh_elements: int = 0
    convergence_time_sec: float = 0.0
    residual_tolerance: float = 1e-6
    max_temperature: float = 0.0
    min_temperature: float = 0.0
    peak_stress: float = 0.0
    stability_threshold_exceeded: bool = False
    sensitivity: Dict[str, float] = field(default_factory=dict)
    run_count: int = 0
    confidence_interval: str = ""
    non_convergent_cases: int = 0
    variance: float = 0.0


class ParameterSampler:
    """Handles parameter perturbation sampling strategies."""
    
    def __init__(self, random_seed: Optional[int] = None):
        self.rng = np.random.RandomState(random_seed)
    
    def generate_perturbations(
        self,
        parameters: List[ParameterConfig],
        method: SamplingMethod,
        num_runs: int
    ) -> List[Dict[str, float]]:
        """
        Generate parameter perturbations based on sampling method.
        
        Returns list of parameter dictionaries, one per run.
        """
        perturbable_params = [p for p in parameters if p.perturbable]
        
        if not perturbable_params:
            logger.warning("No perturbable parameters found")
            return [{p.name: p.base_value for p in parameters} for _ in range(num_runs)]
        
        if method == SamplingMethod.PERCENTAGE_5:
            return self._percentage_sampling(perturbable_params, parameters, 0.05, num_runs)
        elif method == SamplingMethod.PERCENTAGE_10:
            return self._percentage_sampling(perturbable_params, parameters, 0.10, num_runs)
        elif method == SamplingMethod.LATIN_HYPERCUBE:
            return self._latin_hypercube_sampling(perturbable_params, parameters, num_runs)
        else:
            raise ValueError(f"Unknown sampling method: {method}")
    
    def _percentage_sampling(
        self,
        perturbable_params: List[ParameterConfig],
        all_params: List[ParameterConfig],
        percentage: float,
        num_runs: int
    ) -> List[Dict[str, float]]:
        """Generate perturbations using ±percentage variation."""
        perturbations = []
        base_dict = {p.name: p.base_value for p in all_params}
        
        for run_idx in range(num_runs):
            perturbed = base_dict.copy()
            
            for param in perturbable_params:
                # Alternate between + and - perturbation
                if run_idx % 2 == 0:
                    factor = 1 + percentage
                else:
                    factor = 1 - percentage
                
                # Add some randomness within the range for variety
                noise = self.rng.uniform(-0.02, 0.02)
                factor += noise
                
                new_value = param.base_value * factor
                
                # Clamp to bounds if specified
                if param.min_value is not None:
                    new_value = max(new_value, param.min_value)
                if param.max_value is not None:
                    new_value = min(new_value, param.max_value)
                
                perturbed[param.name] = new_value
            
            perturbations.append(perturbed)
        
        return perturbations
    
    def _latin_hypercube_sampling(
        self,
        perturbable_params: List[ParameterConfig],
        all_params: List[ParameterConfig],
        num_runs: int
    ) -> List[Dict[str, float]]:
        """Generate perturbations using Latin Hypercube Sampling."""
        num_params = len(perturbable_params)
        
        # Generate LHS samples in [0, 1] range
        lhs_samples = self._generate_lhs_samples(num_runs, num_params)
        
        perturbations = []
        base_dict = {p.name: p.base_value for p in all_params}
        
        for run_idx in range(num_runs):
            perturbed = base_dict.copy()
            
            for param_idx, param in enumerate(perturbable_params):
                # Map [0, 1] to [0.9, 1.1] for ±10% range
                sample = lhs_samples[run_idx, param_idx]
                factor = 0.9 + sample * 0.2  # Maps to [0.9, 1.1]
                
                new_value = param.base_value * factor
                
                # Clamp to bounds
                if param.min_value is not None:
                    new_value = max(new_value, param.min_value)
                if param.max_value is not None:
                    new_value = min(new_value, param.max_value)
                
                perturbed[param.name] = new_value
            
            perturbations.append(perturbed)
        
        return perturbations
    
    def _generate_lhs_samples(self, n_samples: int, n_params: int) -> np.ndarray:
        """Generate Latin Hypercube Sampling matrix."""
        # Generate random samples within each stratum
        samples = np.zeros((n_samples, n_params))
        
        for j in range(n_params):
            # Generate random permutations for each parameter
            perm = self.rng.permutation(n_samples)
            # Add random offset within each stratum
            samples[:, j] = (perm + self.rng.uniform(0, 1, n_samples)) / n_samples
        
        return samples


class SimulationRunner:
    """
    Interface to MFEM + SUNDIALS simulation runner.
    
    This is a placeholder that would integrate with the actual simulation backend.
    """
    
    def __init__(self):
        self.simulation_count = 0
    
    async def run_simulation(
        self,
        parameters: Dict[str, float],
        run_id: int,
        timeout_sec: float = 300.0
    ) -> SimulationResult:
        """
        Execute a single simulation run.
        
        In production, this would call the actual MFEM + SUNDIALS solver.
        For demonstration, we generate realistic synthetic results.
        """
        self.simulation_count += 1
        start_time = time.time()
        
        # Simulate computation time (1-5 seconds for demo)
        await asyncio.sleep(np.random.uniform(0.1, 0.5))
        
        # Generate realistic results based on parameters
        boundary_flux = parameters.get("boundary_flux", 1000.0)
        thermal_conductivity = parameters.get("thermal_conductivity", 1.0)
        ambient_temp = parameters.get("ambient_temp", 300.0)
        
        # Physics-based approximations for demonstration
        max_temp = ambient_temp + (boundary_flux / thermal_conductivity) * 0.1
        min_temp = ambient_temp
        peak_stress = (max_temp - ambient_temp) * 0.5 + np.random.normal(0, 5)
        
        # Convergence time varies with problem complexity
        convergence_time = 40.0 + np.random.exponential(5.0)
        
        computation_time = time.time() - start_time
        
        return SimulationResult(
            run_id=run_id,
            parameters=parameters,
            convergence_time_sec=convergence_time,
            max_temperature=max_temp,
            min_temperature=min_temp,
            peak_stress=max(0, peak_stress),
            residual_tolerance=1e-6 * (1 + np.random.uniform(0, 0.1)),
            converged=True,
            mesh_elements=2_100_000,
            timestep_count=int(convergence_time * 10)
        )


class StatisticalAnalyzer:
    """Computes sensitivity metrics and statistical summaries."""
    
    def compute_sensitivity_ranking(
        self,
        results: List[SimulationResult],
        baseline: SimulationResult,
        parameters: List[ParameterConfig]
    ) -> List[SensitivityMetric]:
        """
        Compute sensitivity ranking for each parameter.
        
        Uses correlation-based sensitivity analysis.
        """
        if len(results) < 3:
            logger.warning("Insufficient results for sensitivity analysis")
            return []
        
        sensitivities = []
        
        for param in parameters:
            if not param.perturbable:
                continue
            
            # Extract parameter values and corresponding outputs
            param_values = [r.parameters.get(param.name, param.base_value) for r in results]
            max_temps = [r.max_temperature for r in results]
            
            # Compute correlation coefficient as influence measure
            if len(set(param_values)) > 1:
                correlation = np.corrcoef(param_values, max_temps)[0, 1]
                influence = abs(correlation) if not np.isnan(correlation) else 0.0
            else:
                influence = 0.0
            
            # Compute variance contribution
            variance_contrib = self._compute_variance_contribution(
                param_values, max_temps
            )
            
            sensitivities.append(SensitivityMetric(
                parameter_name=param.name,
                influence_coefficient=influence,
                variance_contribution=variance_contrib
            ))
        
        # Sort by influence coefficient and assign ranks
        sensitivities.sort(key=lambda x: x.influence_coefficient, reverse=True)
        for i, sens in enumerate(sensitivities):
            sens.rank = i + 1
        
        return sensitivities
    
    def _compute_variance_contribution(
        self,
        param_values: List[float],
        outputs: List[float]
    ) -> float:
        """Compute variance contribution using simple regression."""
        if len(set(param_values)) <= 1:
            return 0.0
        
        # Simple linear regression
        x = np.array(param_values)
        y = np.array(outputs)
        
        x_mean, y_mean = np.mean(x), np.mean(y)
        ss_xy = np.sum((x - x_mean) * (y - y_mean))
        ss_xx = np.sum((x - x_mean) ** 2)
        
        if ss_xx == 0:
            return 0.0
        
        slope = ss_xy / ss_xx
        y_pred = slope * x + (y_mean - slope * x_mean)
        
        ss_tot = np.sum((y - y_mean) ** 2)
        ss_res = np.sum((y - y_pred) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return max(0, r_squared)
    
    def compute_confidence_interval(
        self,
        results: List[SimulationResult],
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Compute confidence interval for max temperature.
        
        Returns: (mean, margin_of_error, percentage)
        """
        if not results:
            return 0.0, 0.0, 0.0
        
        max_temps = [r.max_temperature for r in results if r.converged]
        
        if len(max_temps) < 2:
            return max_temps[0] if max_temps else 0.0, 0.0, 0.0
        
        mean = np.mean(max_temps)
        std = np.std(max_temps, ddof=1)
        n = len(max_temps)
        
        # t-distribution critical value (approximate for 95%)
        t_value = 2.0 if confidence == 0.95 else 1.96
        
        margin_of_error = t_value * (std / np.sqrt(n))
        percentage = (margin_of_error / mean) * 100 if mean != 0 else 0.0
        
        return mean, margin_of_error, percentage
    
    def compute_variance(self, results: List[SimulationResult]) -> float:
        """Compute variance of max temperature across runs."""
        max_temps = [r.max_temperature for r in results if r.converged]
        return np.var(max_temps, ddof=1) if len(max_temps) > 1 else 0.0
    
    def compute_standard_deviation(self, results: List[SimulationResult]) -> float:
        """Compute standard deviation of max temperature across runs."""
        max_temps = [r.max_temperature for r in results if r.converged]
        return np.std(max_temps, ddof=1) if len(max_temps) > 1 else 0.0


class RobustnessService:
    """
    Main service orchestrating robustness analysis.
    
    Responsibilities:
    - Parameter sampling logic
    - Job batching
    - Result aggregation
    - Statistical summary
    """
    
    def __init__(
        self,
        simulation_runner: Optional[SimulationRunner] = None,
        max_concurrent_runs: int = 4
    ):
        self.sampler = ParameterSampler()
        self.runner = simulation_runner or SimulationRunner()
        self.analyzer = StatisticalAnalyzer()
        self.max_concurrent = max_concurrent_runs
    
    async def run_robustness_analysis(
        self,
        config: RobustnessConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> RobustnessSummary:
        """
        Execute complete robustness analysis workflow.
        
        1. Generate parameter perturbations
        2. Run baseline simulation
        3. Spawn N simulation runs
        4. Collect outputs
        5. Compute metrics
        6. Return structured result
        """
        if not config.enabled:
            raise ValueError("Robustness analysis is disabled")
        
        start_time = time.time()
        logger.info(f"Starting robustness analysis: {config.num_runs} runs")
        
        # Step 1: Generate perturbations
        perturbations = self.sampler.generate_perturbations(
            config.parameters,
            config.sampling_method,
            config.num_runs
        )
        
        # Step 2: Run baseline simulation (first run with base parameters)
        baseline_params = {p.name: p.base_value for p in config.parameters}
        logger.info("Running baseline simulation...")
        baseline_result = await self.runner.run_simulation(
            baseline_params, run_id=0, timeout_sec=config.convergence_timeout_sec
        )
        
        # Step 3 & 4: Spawn N simulation runs with batching
        all_results = [baseline_result]
        
        # Process in batches
        remaining = list(range(1, config.num_runs))
        completed = 1
        
        while remaining:
            batch = remaining[:self.max_concurrent]
            remaining = remaining[self.max_concurrent:]
            
            # Run batch concurrently
            tasks = [
                self.runner.run_simulation(
                    perturbations[i], run_id=i, timeout_sec=config.convergence_timeout_sec
                )
                for i in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Simulation failed: {result}")
                    # Create failed result placeholder
                    failed_result = SimulationResult(
                        run_id=-1,
                        parameters={},
                        convergence_time_sec=0.0,
                        max_temperature=0.0,
                        min_temperature=0.0,
                        peak_stress=0.0,
                        residual_tolerance=0.0,
                        converged=False,
                        failure_reason=str(result)
                    )
                    all_results.append(failed_result)
                else:
                    all_results.append(result)
                completed += 1
            
            if progress_callback:
                progress_callback(completed, config.num_runs)
            
            logger.info(f"Completed {completed}/{config.num_runs} runs")
        
        # Step 5: Compute metrics
        sensitivity_ranking = self.analyzer.compute_sensitivity_ranking(
            all_results, baseline_result, config.parameters
        )
        
        mean, margin, confidence_pct = self.analyzer.compute_confidence_interval(
            all_results
        )
        
        variance = self.analyzer.compute_variance(all_results)
        std_dev = self.analyzer.compute_standard_deviation(all_results)
        
        non_convergent = sum(1 for r in all_results if not r.converged)
        
        computation_time = time.time() - start_time
        
        summary = RobustnessSummary(
            baseline_result=baseline_result,
            all_results=all_results,
            sensitivity_ranking=sensitivity_ranking,
            confidence_interval_percent=confidence_pct,
            variance=variance,
            standard_deviation=std_dev,
            non_convergent_count=non_convergent,
            run_count=len(all_results),
            sampling_method=config.sampling_method.value,
            computation_time_sec=computation_time
        )
        
        logger.info(f"Robustness analysis complete in {computation_time:.2f}s")
        return summary
    
    def create_ai_report_input(
        self,
        summary: RobustnessSummary
    ) -> AIReportInput:
        """
        Create structured input for AI report generation.
        
        Never send raw mesh fields - only structured metrics.
        """
        baseline = summary.baseline_result
        
        sensitivity_dict = {
            s.parameter_name: round(s.influence_coefficient, 2)
            for s in summary.sensitivity_ranking
        }
        
        return AIReportInput(
            solver="MFEM + SUNDIALS",
            mesh_elements=baseline.mesh_elements,
            convergence_time_sec=baseline.convergence_time_sec,
            residual_tolerance=baseline.residual_tolerance,
            max_temperature=round(baseline.max_temperature, 1),
            min_temperature=round(baseline.min_temperature, 1),
            peak_stress=round(baseline.peak_stress, 1),
            stability_threshold_exceeded=baseline.peak_stress > 200.0,  # Example threshold
            sensitivity=sensitivity_dict,
            run_count=summary.run_count,
            confidence_interval=f"±{summary.confidence_interval_percent:.1f}%",
            non_convergent_cases=summary.non_convergent_count,
            variance=summary.variance
        )


# Singleton instance for application use
_robustness_service: Optional[RobustnessService] = None


def get_robustness_service() -> RobustnessService:
    """Get or create the singleton robustness service instance."""
    global _robustness_service
    if _robustness_service is None:
        _robustness_service = RobustnessService()
    return _robustness_service


def reset_robustness_service():
    """Reset the singleton instance (useful for testing)."""
    global _robustness_service
    _robustness_service = None


# Example usage and demonstration
if __name__ == "__main__":
    async def demo():
        """Demonstrate robustness analysis workflow."""
        
        # Define parameters
        params = [
            ParameterConfig(
                name="boundary_flux",
                base_value=1000.0,
                unit="W/m²",
                description="Heat flux at boundary",
                perturbable=True,
                min_value=500.0,
                max_value=1500.0
            ),
            ParameterConfig(
                name="thermal_conductivity",
                base_value=1.0,
                unit="W/(m·K)",
                description="Material thermal conductivity",
                perturbable=True,
                min_value=0.5,
                max_value=2.0
            ),
            ParameterConfig(
                name="ambient_temp",
                base_value=300.0,
                unit="K",
                description="Ambient temperature",
                perturbable=True,
                min_value=250.0,
                max_value=350.0
            ),
            ParameterConfig(
                name="mesh_refinement",
                base_value=2.0,
                unit="level",
                description="Mesh refinement level",
                perturbable=False
            )
        ]
        
        # Configure robustness analysis
        config = RobustnessConfig(
            enabled=True,
            num_runs=15,
            sampling_method=SamplingMethod.PERCENTAGE_10,
            parameters=params,
            random_seed=42
        )
        
        # Create service and run analysis
        service = RobustnessService()
        
        def progress(current, total):
            print(f"Progress: {current}/{total} runs complete")
        
        summary = await service.run_robustness_analysis(config, progress)
        
        # Print results
        print("\n" + "="*60)
        print("ROBUSTNESS ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\nBaseline Result:")
        print(f"  Max Temperature: {summary.baseline_result.max_temperature:.1f} K")
        print(f"  Peak Stress: {summary.baseline_result.peak_stress:.1f} MPa")
        print(f"  Convergence Time: {summary.baseline_result.convergence_time_sec:.1f} sec")
        
        print(f"\nSensitivity Ranking:")
        for s in summary.sensitivity_ranking:
            print(f"  {s.rank}. {s.parameter_name}: {s.influence_coefficient:.2f}")
        
        print(f"\nStatistical Summary:")
        print(f"  Confidence Interval: ±{summary.confidence_interval_percent:.1f}%")
        print(f"  Variance: {summary.variance:.2f}")
        print(f"  Non-convergent cases: {summary.non_convergent_count}")
        print(f"  Total computation time: {summary.computation_time_sec:.2f}s")
        
        # Generate AI report input
        ai_input = service.create_ai_report_input(summary)
        print(f"\nAI Report Input (JSON):")
        print(json.dumps(asdict(ai_input), indent=2))
    
    asyncio.run(demo())
