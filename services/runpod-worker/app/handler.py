import runpod
from app.robustness_service import RobustnessService


def handler(job):
    job_input = job.get("input", job)

    if job_input.get("check_health_only"):
        return {"status": "ready", "version": "1.6.0-ALPHA"}

    service = RobustnessService()
    result = service.run_robustness_analysis(job_input)
    return result


runpod.serverless.start({"handler": handler})
