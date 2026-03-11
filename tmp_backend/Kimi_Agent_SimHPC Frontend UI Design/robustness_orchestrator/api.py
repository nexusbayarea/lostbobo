"""
Robustness Orchestrator API

FastAPI backend providing endpoints for robustness analysis and AI reporting.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

from robustness_service import (
    RobustnessService,
    RobustnessConfig,
    ParameterConfig,
    SamplingMethod,
    get_robustness_service,
    AIReportInput
)
from ai_report_service import (
    AIReportService,
    get_ai_report_service,
    AIReport
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API
class ParameterConfigModel(BaseModel):
    name: str
    base_value: float
    unit: str = ""
    description: str = ""
    perturbable: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class RobustnessConfigModel(BaseModel):
    enabled: bool = False
    num_runs: int = Field(default=15, ge=5, le=50)
    sampling_method: str = "±10%"
    parameters: List[ParameterConfigModel]
    convergence_timeout_sec: float = 300.0
    random_seed: Optional[int] = None


class RunSimulationRequest(BaseModel):
    config: RobustnessConfigModel
    run_name: Optional[str] = None


class SimulationResultModel(BaseModel):
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


class SensitivityMetricModel(BaseModel):
    parameter_name: str
    influence_coefficient: float
    variance_contribution: float
    rank: int


class RobustnessSummaryModel(BaseModel):
    baseline_result: SimulationResultModel
    all_results: List[SimulationResultModel]
    sensitivity_ranking: List[SensitivityMetricModel]
    confidence_interval_percent: float
    variance: float
    standard_deviation: float
    non_convergent_count: int
    run_count: int
    sampling_method: str
    computation_time_sec: float


class AIReportSectionModel(BaseModel):
    title: str
    content: str
    order: int


class AIReportModel(BaseModel):
    report_id: str
    generated_at: str
    sections: List[AIReportSectionModel]
    disclaimer: str
    metadata: Dict[str, Any]


class RunStatus(BaseModel):
    run_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: Dict[str, int]  # {"current": 5, "total": 15}
    created_at: str
    completed_at: Optional[str] = None
    results: Optional[RobustnessSummaryModel] = None
    ai_report: Optional[AIReportModel] = None


# In-memory store for run status (use database in production)
_run_store: Dict[str, RunStatus] = {}


def _sampling_method_from_string(method_str: str) -> SamplingMethod:
    """Convert string to SamplingMethod enum."""
    mapping = {
        "±5%": SamplingMethod.PERCENTAGE_5,
        "±10%": SamplingMethod.PERCENTAGE_10,
        "latin_hypercube": SamplingMethod.LATIN_HYPERCUBE,
        "Latin Hypercube": SamplingMethod.LATIN_HYPERCUBE,
    }
    return mapping.get(method_str, SamplingMethod.PERCENTAGE_10)


def _convert_to_robustness_config(model: RobustnessConfigModel) -> RobustnessConfig:
    """Convert Pydantic model to internal config."""
    return RobustnessConfig(
        enabled=model.enabled,
        num_runs=model.num_runs,
        sampling_method=_sampling_method_from_string(model.sampling_method),
        parameters=[
            ParameterConfig(
                name=p.name,
                base_value=p.base_value,
                unit=p.unit,
                description=p.description,
                perturbable=p.perturbable,
                min_value=p.min_value,
                max_value=p.max_value
            )
            for p in model.parameters
        ],
        convergence_timeout_sec=model.convergence_timeout_sec,
        random_seed=model.random_seed
    )


def _convert_simulation_result(result: Any) -> SimulationResultModel:
    """Convert internal result to Pydantic model."""
    return SimulationResultModel(
        run_id=result.run_id,
        parameters=result.parameters,
        convergence_time_sec=result.convergence_time_sec,
        max_temperature=result.max_temperature,
        min_temperature=result.min_temperature,
        peak_stress=result.peak_stress,
        residual_tolerance=result.residual_tolerance,
        converged=result.converged,
        failure_reason=result.failure_reason,
        mesh_elements=result.mesh_elements,
        timestep_count=result.timestep_count
    )


def _convert_sensitivity_metric(metric: Any) -> SensitivityMetricModel:
    """Convert internal metric to Pydantic model."""
    return SensitivityMetricModel(
        parameter_name=metric.parameter_name,
        influence_coefficient=metric.influence_coefficient,
        variance_contribution=metric.variance_contribution,
        rank=metric.rank
    )


def _convert_robustness_summary(summary: Any) -> RobustnessSummaryModel:
    """Convert internal summary to Pydantic model."""
    return RobustnessSummaryModel(
        baseline_result=_convert_simulation_result(summary.baseline_result),
        all_results=[_convert_simulation_result(r) for r in summary.all_results],
        sensitivity_ranking=[_convert_sensitivity_metric(s) for s in summary.sensitivity_ranking],
        confidence_interval_percent=summary.confidence_interval_percent,
        variance=summary.variance,
        standard_deviation=summary.standard_deviation,
        non_convergent_count=summary.non_convergent_count,
        run_count=summary.run_count,
        sampling_method=summary.sampling_method,
        computation_time_sec=summary.computation_time_sec
    )


def _convert_ai_report(report: AIReport) -> AIReportModel:
    """Convert AI report to Pydantic model."""
    return AIReportModel(
        report_id=report.report_id,
        generated_at=report.generated_at,
        sections=[
            AIReportSectionModel(title=s.title, content=s.content, order=s.order)
            for s in report.sections
        ],
        disclaimer=report.disclaimer,
        metadata=report.metadata
    )


# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Robustness Orchestrator API")
    yield
    logger.info("Shutting down Robustness Orchestrator API")


app = FastAPI(
    title="Robustness Orchestrator API",
    description="API for parameter variation analysis and AI interpretation of MFEM + SUNDIALS simulations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "service": "Robustness Orchestrator API",
        "version": "1.0.0",
        "physics_engine": "MFEM + SUNDIALS",
        "ai_layer": "Advisory only - no solver modification"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/robustness/run", response_model=RunStatus)
async def start_robustness_run(request: RunSimulationRequest, background_tasks: BackgroundTasks):
    """
    Start a new robustness analysis run.
    
    The run executes in the background. Use /api/v1/robustness/status/{run_id} to check progress.
    """
    if not request.config.enabled:
        raise HTTPException(status_code=400, detail="Robustness analysis is disabled. Set enabled=true to run.")
    
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(request) % 10000:04d}"
    
    # Initialize run status
    _run_store[run_id] = RunStatus(
        run_id=run_id,
        status="pending",
        progress={"current": 0, "total": request.config.num_runs},
        created_at=datetime.utcnow().isoformat()
    )
    
    # Start background task
    background_tasks.add_task(_execute_robustness_run, run_id, request)
    
    logger.info(f"Started robustness run: {run_id}")
    return _run_store[run_id]


async def _execute_robustness_run(run_id: str, request: RunSimulationRequest):
    """Execute robustness analysis in background."""
    try:
        _run_store[run_id].status = "running"
        
        # Get services
        robustness_service = get_robustness_service()
        ai_service = get_ai_report_service()
        
        # Convert config
        config = _convert_to_robustness_config(request.config)
        
        # Progress callback
        def update_progress(current: int, total: int):
            _run_store[run_id].progress = {"current": current, "total": total}
        
        # Run analysis
        summary = await robustness_service.run_robustness_analysis(config, update_progress)
        
        # Convert to API model
        summary_model = _convert_robustness_summary(summary)
        
        # Generate AI report
        ai_input = robustness_service.create_ai_report_input(summary)
        ai_input_dict = {
            "solver": ai_input.solver,
            "mesh_elements": ai_input.mesh_elements,
            "convergence_time_sec": ai_input.convergence_time_sec,
            "residual_tolerance": ai_input.residual_tolerance,
            "max_temperature": ai_input.max_temperature,
            "min_temperature": ai_input.min_temperature,
            "peak_stress": ai_input.peak_stress,
            "stability_threshold_exceeded": ai_input.stability_threshold_exceeded,
            "sensitivity": ai_input.sensitivity,
            "run_count": ai_input.run_count,
            "confidence_interval": ai_input.confidence_interval,
            "non_convergent_cases": ai_input.non_convergent_cases,
            "variance": ai_input.variance
        }
        
        ai_report = ai_service.generate_report(ai_input_dict)
        ai_report_model = _convert_ai_report(ai_report)
        
        # Update run status
        _run_store[run_id].status = "completed"
        _run_store[run_id].completed_at = datetime.utcnow().isoformat()
        _run_store[run_id].results = summary_model
        _run_store[run_id].ai_report = ai_report_model
        
        logger.info(f"Completed robustness run: {run_id}")
        
    except Exception as e:
        logger.error(f"Robustness run failed: {e}")
        _run_store[run_id].status = "failed"
        _run_store[run_id].completed_at = datetime.utcnow().isoformat()


@app.get("/api/v1/robustness/status/{run_id}", response_model=RunStatus)
async def get_run_status(run_id: str):
    """Get status of a robustness analysis run."""
    if run_id not in _run_store:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return _run_store[run_id]


@app.get("/api/v1/robustness/runs")
async def list_runs():
    """List all robustness analysis runs."""
    return {
        "runs": [
            {
                "run_id": r.run_id,
                "status": r.status,
                "created_at": r.created_at,
                "completed_at": r.completed_at
            }
            for r in _run_store.values()
        ]
    }


@app.get("/api/v1/robustness/results/{run_id}")
async def get_run_results(run_id: str):
    """Get detailed results of a completed run."""
    if run_id not in _run_store:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    run = _run_store[run_id]
    if run.status != "completed":
        raise HTTPException(status_code=400, detail=f"Run {run_id} is not completed (status: {run.status})")
    
    return {
        "run_id": run_id,
        "results": run.results,
        "ai_report": run.ai_report
    }


@app.get("/api/v1/robustness/report/{run_id}/markdown")
async def get_ai_report_markdown(run_id: str):
    """Get AI report in Markdown format."""
    if run_id not in _run_store:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    run = _run_store[run_id]
    if not run.ai_report:
        raise HTTPException(status_code=400, detail=f"AI report not available for run {run_id}")
    
    # Reconstruct AIReport object for markdown conversion
    report = AIReport(
        report_id=run.ai_report.report_id,
        generated_at=run.ai_report.generated_at,
        sections=[
            type('Section', (), s) for s in run.ai_report.sections
        ],
        disclaimer=run.ai_report.disclaimer,
        metadata=run.ai_report.metadata
    )
    
    return {"markdown": report.to_markdown()}


@app.post("/api/v1/ai/report")
async def generate_ai_report_direct(simulation_data: Dict[str, Any]):
    """
    Generate AI report directly from simulation data.
    
    This endpoint bypasses the robustness analysis and generates
    an interpretive report from provided structured data.
    """
    try:
        ai_service = get_ai_report_service()
        report = ai_service.generate_report(simulation_data)
        return _convert_ai_report(report)
    except Exception as e:
        logger.error(f"AI report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sampling-methods")
async def get_sampling_methods():
    """Get available sampling methods."""
    return {
        "methods": [
            {"id": "±5%", "name": "±5% Perturbation", "description": "Uniform ±5% parameter variation"},
            {"id": "±10%", "name": "±10% Perturbation", "description": "Uniform ±10% parameter variation"},
            {"id": "latin_hypercube", "name": "Latin Hypercube Sampling", "description": "Statistically efficient space-filling design"}
        ]
    }


# Example parameter presets
PARAMETER_PRESETS = {
    "thermal_analysis": [
        ParameterConfigModel(
            name="boundary_flux",
            base_value=1000.0,
            unit="W/m²",
            description="Heat flux at boundary",
            perturbable=True,
            min_value=500.0,
            max_value=1500.0
        ),
        ParameterConfigModel(
            name="thermal_conductivity",
            base_value=1.0,
            unit="W/(m·K)",
            description="Material thermal conductivity",
            perturbable=True,
            min_value=0.5,
            max_value=2.0
        ),
        ParameterConfigModel(
            name="ambient_temp",
            base_value=300.0,
            unit="K",
            description="Ambient temperature",
            perturbable=True,
            min_value=250.0,
            max_value=350.0
        ),
        ParameterConfigModel(
            name="mesh_refinement",
            base_value=2.0,
            unit="level",
            description="Mesh refinement level",
            perturbable=False
        )
    ],
    "structural_analysis": [
        ParameterConfigModel(
            name="youngs_modulus",
            base_value=200e9,
            unit="Pa",
            description="Young's modulus",
            perturbable=True,
            min_value=180e9,
            max_value=220e9
        ),
        ParameterConfigModel(
            name="poisson_ratio",
            base_value=0.3,
            unit="",
            description="Poisson's ratio",
            perturbable=True,
            min_value=0.25,
            max_value=0.35
        ),
        ParameterConfigModel(
            name="applied_load",
            base_value=10000.0,
            unit="N",
            description="Applied load",
            perturbable=True,
            min_value=5000.0,
            max_value=15000.0
        )
    ]
}


@app.get("/api/v1/parameter-presets")
async def get_parameter_presets():
    """Get available parameter presets."""
    return {
        "presets": {
            name: [p.model_dump() for p in params]
            for name, params in PARAMETER_PRESETS.items()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
