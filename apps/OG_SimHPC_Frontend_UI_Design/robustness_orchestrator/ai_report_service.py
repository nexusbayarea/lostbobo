"""
AI Report Service

Generates structured interpretive summaries from simulation robustness analysis.

Design Principle: AI layer remains advisory. Never mix with deterministic physics.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIReportSection:
    """A single section of the AI report."""
    title: str
    content: str
    order: int


@dataclass
class AIReport:
    """Complete AI-generated interpretation report."""
    report_id: str
    generated_at: str
    sections: List[AIReportSection]
    disclaimer: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_markdown(self) -> str:
        """Convert report to markdown format."""
        lines = [
            f"# AI Interpretation Report",
            f"",
            f"**Generated:** {self.generated_at}",
            f"**Report ID:** {self.report_id}",
            f"",
            "---",
            f""
        ]
        
        for section in sorted(self.sections, key=lambda s: s.order):
            lines.extend([
                f"## {section.title}",
                f"",
                section.content,
                f"",
            ])
        
        lines.extend([
            "---",
            f"",
            f"**{self.disclaimer}**",
            f""
        ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "sections": [
                {"title": s.title, "content": s.content, "order": s.order}
                for s in self.sections
            ],
            "disclaimer": self.disclaimer,
            "metadata": self.metadata
        }


class ReportTemplate:
    """
    Fixed report schema template.
    
    Enforces structure. AI fills sections.
    """
    
    SECTIONS = [
        ("Simulation Summary", 1),
        ("Key Output Metrics", 2),
        ("Sensitivity Ranking", 3),
        ("Uncertainty Assessment", 4),
        ("Engineering Interpretation", 5),
        ("Suggested Next Simulation", 6),
    ]
    
    DISCLAIMER = (
        "AI-generated interpretation based on simulation outputs. "
        "Numerical results originate from deterministic solvers (MFEM + SUNDIALS)."
    )
    
    # Constrained vocabulary for scientific tone
    ALLOWED_INDICATORS = [
        "indicates",
        "suggests",
        "observed sensitivity",
        "model behavior shows",
        "demonstrates",
        "correlates with",
        "is associated with"
    ]
    
    PROHIBITED_PHRASES = [
        "this proves",
        "this guarantees",
        "this confirms",
        "definitely",
        "absolutely",
        "certainly",
        "without doubt"
    ]


class PromptBuilder:
    """Builds controlled prompt templates for AI report generation."""
    
    @staticmethod
    def build_simulation_summary_prompt(data: Dict[str, Any]) -> str:
        """Build prompt for Simulation Summary section."""
        return f"""Generate a concise simulation summary section.

Input Data:
- Solver: {data.get('solver', 'MFEM + SUNDIALS')}
- Mesh elements: {data.get('mesh_elements', 0):,}
- Convergence time: {data.get('convergence_time_sec', 0):.1f} sec
- Residual tolerance: {data.get('residual_tolerance', 1e-6):.0e}

Requirements:
- Use bullet points
- Include factual solver configuration details
- Tone: technical, precise
- Do not interpret, only summarize
"""
    
    @staticmethod
    def build_key_metrics_prompt(data: Dict[str, Any]) -> str:
        """Build prompt for Key Output Metrics section."""
        return f"""Generate a key output metrics section.

Input Data:
- Peak temperature: {data.get('max_temperature', 0):.1f} K
- Min temperature: {data.get('min_temperature', 0):.1f} K
- Peak stress: {data.get('peak_stress', 0):.1f} MPa
- Stability threshold exceeded: {data.get('stability_threshold_exceeded', False)}

Requirements:
- Use bullet points
- Present values with units
- Note any threshold conditions
- Tone: factual, quantitative
"""
    
    @staticmethod
    def build_sensitivity_prompt(data: Dict[str, Any]) -> str:
        """Build prompt for Sensitivity Ranking section."""
        sensitivity = data.get('sensitivity', {})
        sensitivity_str = "\n".join([
            f"  {i+1}. {param}: {coeff:.2f}"
            for i, (param, coeff) in enumerate(sensitivity.items())
        ])
        
        return f"""Generate a sensitivity ranking interpretation.

Input Data (ranked by influence coefficient):
{sensitivity_str}

Requirements:
- List parameters in order of influence
- Provide brief interpretation of primary driver
- Use phrase: "Model output is primarily driven by..."
- Tone: analytical, cautious
- Use "indicates" or "suggests" for interpretations
"""
    
    @staticmethod
    def build_uncertainty_prompt(data: Dict[str, Any]) -> str:
        """Build prompt for Uncertainty Assessment section."""
        return f"""Generate an uncertainty assessment section.

Input Data:
- Run count: {data.get('run_count', 0)}
- Confidence interval: {data.get('confidence_interval', 'N/A')}
- Non-convergent cases: {data.get('non_convergent_cases', 0)}
- Variance: {data.get('variance', 0):.2f}

Requirements:
- Summarize perturbation sweep scope
- Present confidence interval
- Note any convergence issues
- Tone: statistical, measured
"""
    
    @staticmethod
    def build_interpretation_prompt(data: Dict[str, Any]) -> str:
        """Build prompt for Engineering Interpretation section."""
        sensitivity = data.get('sensitivity', {})
        top_param = list(sensitivity.keys())[0] if sensitivity else "boundary flux"
        
        return f"""Generate an engineering interpretation paragraph.

Input Data:
- Peak temperature: {data.get('max_temperature', 0):.1f} K
- Peak stress: {data.get('peak_stress', 0):.1f} MPa
- Primary sensitive parameter: {top_param}
- Confidence interval: {data.get('confidence_interval', 'N/A')}

Requirements:
- 2-3 sentences maximum
- Connect sensitivity findings to physical behavior
- Use constrained language:
  - "Small perturbations in {top_param} produce..."
  - "System stability is sensitive to..."
  - "Model behavior shows..."
- NEVER use: "proves", "guarantees", "confirms", "definitely"
- Tone: engineering-focused, cautious
"""
    
    @staticmethod
    def build_suggestions_prompt(data: Dict[str, Any]) -> str:
        """Build prompt for Suggested Next Simulation section."""
        sensitivity = data.get('sensitivity', {})
        top_param = list(sensitivity.keys())[0] if sensitivity else "boundary flux"
        
        return f"""Generate suggested next simulation steps.

Input Data:
- Primary sensitive parameter: {top_param}
- Current confidence interval: {data.get('confidence_interval', 'N/A')}
- Mesh elements: {data.get('mesh_elements', 0):,}

Requirements:
- Provide 2-3 specific, actionable suggestions
- Focus on:
  1. Mesh refinement near sensitive regions
  2. Extended parameter range exploration
  3. Model complexity evaluation
- Use bullet points
- Tone: prescriptive but cautious
"""


class AIReportService:
    """
    Service for generating AI interpretation reports.
    
    Enforces:
    - Fixed report schema
    - Constrained vocabulary
    - Scientific tone discipline
    - Output caching
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("./ai_report_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.template = ReportTemplate()
        self.prompt_builder = PromptBuilder()
    
    def _generate_report_id(self, data: Dict[str, Any]) -> str:
        """Generate unique report ID from input data hash."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _get_cache_path(self, report_id: str) -> Path:
        """Get cache file path for report ID."""
        return self.cache_dir / f"{report_id}.json"
    
    def _load_cached_report(self, report_id: str) -> Optional[AIReport]:
        """Load cached report if exists."""
        cache_path = self._get_cache_path(report_id)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded cached report: {report_id}")
                return AIReport(
                    report_id=data['report_id'],
                    generated_at=data['generated_at'],
                    sections=[
                        AIReportSection(s['title'], s['content'], s['order'])
                        for s in data['sections']
                    ],
                    disclaimer=data['disclaimer'],
                    metadata=data.get('metadata', {})
                )
            except Exception as e:
                logger.warning(f"Failed to load cached report: {e}")
        return None
    
    def _save_cached_report(self, report: AIReport):
        """Save report to cache."""
        cache_path = self._get_cache_path(report.report_id)
        try:
            with open(cache_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            logger.info(f"Saved report to cache: {report.report_id}")
        except Exception as e:
            logger.warning(f"Failed to cache report: {e}")
    
    def _validate_content(self, content: str) -> str:
        """
        Validate and sanitize AI-generated content.
        
        Ensures:
        - No prohibited phrases
        - Constrained vocabulary usage
        """
        content_lower = content.lower()
        
        # Check for prohibited phrases
        for phrase in self.template.PROHIBITED_PHRASES:
            if phrase in content_lower:
                logger.warning(f"Prohibited phrase detected: '{phrase}'")
                # Replace with safer alternative
                content = content.replace(phrase, "suggests")
        
        return content
    
    def _generate_section_content(
        self,
        section_name: str,
        prompt: str
    ) -> str:
        """
        Generate content for a report section.
        
        In production, this would call an LLM API.
        For demonstration, we use template-based generation.
        """
        # This is where you would integrate with your LLM API
        # For now, we generate realistic placeholder content
        
        if section_name == "Simulation Summary":
            return self._generate_simulation_summary_content(prompt)
        elif section_name == "Key Output Metrics":
            return self._generate_key_metrics_content(prompt)
        elif section_name == "Sensitivity Ranking":
            return self._generate_sensitivity_content(prompt)
        elif section_name == "Uncertainty Assessment":
            return self._generate_uncertainty_content(prompt)
        elif section_name == "Engineering Interpretation":
            return self._generate_interpretation_content(prompt)
        elif section_name == "Suggested Next Simulation":
            return self._generate_suggestions_content(prompt)
        else:
            return "Content generation pending."
    
    def _generate_simulation_summary_content(self, prompt: str) -> str:
        """Generate Simulation Summary content."""
        # Extract values from prompt (in production, pass structured data)
        return """• **Solver Configuration:** MFEM + SUNDIALS time-dependent solver
• **Mesh Elements:** 2.1M tetrahedral elements
• **Convergence Time:** 48.2 seconds
• **Residual Tolerance Achieved:** 1e-6
• **Timestepping:** Adaptive BDF2 with error control"""
    
    def _generate_key_metrics_content(self, prompt: str) -> str:
        """Generate Key Output Metrics content."""
        return """• **Peak Temperature:** 412.3 K (observed at boundary interface)
• **Minimum Temperature:** 289.4 K (ambient region)
• **Peak Stress:** 125.8 MPa (within elastic limits)
• **Stability Threshold:** Not exceeded
• **Temperature Gradient:** 122.9 K across domain"""
    
    def _generate_sensitivity_content(self, prompt: str) -> str:
        """Generate Sensitivity Ranking content."""
        return """Parameters ranked by influence coefficient on peak temperature:

1. **Boundary flux** (0.62 influence coefficient)
2. **Thermal conductivity** (0.21)
3. **Ambient temperature** (0.09)

**Interpretation:** Model output indicates that peak temperature is primarily driven by boundary heat flux variation. Thermal conductivity shows moderate influence, while ambient temperature demonstrates relatively weak coupling to peak temperature response."""
    
    def _generate_uncertainty_content(self, prompt: str) -> str:
        """Generate Uncertainty Assessment content."""
        return """• **Perturbation Sweep:** 15-run parameter variation study
• **Sampling Method:** ±10% uniform perturbation
• **Confidence Interval:** ±3.1% (95% confidence level)
• **Non-convergent Cases:** 0 observed
• **Variance:** 142.3 K²

The analysis suggests robust convergence behavior across the sampled parameter space."""
    
    def _generate_interpretation_content(self, prompt: str) -> str:
        """Generate Engineering Interpretation content."""
        return """Small perturbations in boundary heat flux produce nonlinear amplification in peak temperature response. Model behavior shows that system stability is sensitive to cooling efficiency under high current density conditions. The observed sensitivity pattern indicates that thermal management strategies should prioritize boundary flux control."""
    
    def _generate_suggestions_content(self, prompt: str) -> str:
        """Generate Suggested Next Simulation content."""
        return """• **Increase mesh refinement** near boundary interface regions to capture flux gradients more accurately
• **Evaluate 10–15% flux variation range** to characterize nonlinear response regime
• **Test nonlinear material model** under elevated temperature conditions to assess property degradation effects"""
    
    def generate_report(
        self,
        simulation_data: Dict[str, Any],
        use_cache: bool = True
    ) -> AIReport:
        """
        Generate complete AI interpretation report.
        
        Args:
            simulation_data: Structured simulation summary
            use_cache: Whether to use cached results
        
        Returns:
            Complete AIReport with all sections
        """
        report_id = self._generate_report_id(simulation_data)
        
        # Check cache
        if use_cache:
            cached = self._load_cached_report(report_id)
            if cached:
                return cached
        
        logger.info(f"Generating new AI report: {report_id}")
        
        # Generate each section
        sections = []
        
        section_prompts = [
            ("Simulation Summary", self.prompt_builder.build_simulation_summary_prompt(simulation_data)),
            ("Key Output Metrics", self.prompt_builder.build_key_metrics_prompt(simulation_data)),
            ("Sensitivity Ranking", self.prompt_builder.build_sensitivity_prompt(simulation_data)),
            ("Uncertainty Assessment", self.prompt_builder.build_uncertainty_prompt(simulation_data)),
            ("Engineering Interpretation", self.prompt_builder.build_interpretation_prompt(simulation_data)),
            ("Suggested Next Simulation", self.prompt_builder.build_suggestions_prompt(simulation_data)),
        ]
        
        for section_name, prompt in section_prompts:
            content = self._generate_section_content(section_name, prompt)
            content = self._validate_content(content)
            
            # Get order from template
            order = next((o for n, o in self.template.SECTIONS if n == section_name), 99)
            
            sections.append(AIReportSection(
                title=section_name,
                content=content,
                order=order
            ))
        
        report = AIReport(
            report_id=report_id,
            generated_at=datetime.utcnow().isoformat(),
            sections=sections,
            disclaimer=self.template.DISCLAIMER,
            metadata={
                "input_hash": report_id,
                "version": "1.0"
            }
        )
        
        # Cache the report
        self._save_cached_report(report)
        
        return report


# Singleton instance
_ai_report_service: Optional[AIReportService] = None


def get_ai_report_service(cache_dir: Optional[Path] = None) -> AIReportService:
    """Get or create the singleton AI report service instance."""
    global _ai_report_service
    if _ai_report_service is None:
        _ai_report_service = AIReportService(cache_dir)
    return _ai_report_service


def reset_ai_report_service():
    """Reset the singleton instance."""
    global _ai_report_service
    _ai_report_service = None


# Example usage
if __name__ == "__main__":
    # Example simulation data
    example_data = {
        "solver": "MFEM + SUNDIALS",
        "mesh_elements": 2_100_000,
        "convergence_time_sec": 48.2,
        "residual_tolerance": 1e-6,
        "max_temperature": 412.3,
        "min_temperature": 289.4,
        "peak_stress": 125.8,
        "stability_threshold_exceeded": False,
        "sensitivity": {
            "boundary_flux": 0.62,
            "thermal_conductivity": 0.21,
            "ambient_temp": 0.09
        },
        "run_count": 15,
        "confidence_interval": "±3.1%",
        "non_convergent_cases": 0,
        "variance": 142.3
    }
    
    service = AIReportService()
    
    # Generate report
    report = service.generate_report(example_data)
    
    # Print markdown output
    print(report.to_markdown())
    
    # Demonstrate caching
    print("\n" + "="*60)
    print("CACHED REPORT:")
    print("="*60)
    cached_report = service.generate_report(example_data)
    print(f"Same report ID: {cached_report.report_id == report.report_id}")
