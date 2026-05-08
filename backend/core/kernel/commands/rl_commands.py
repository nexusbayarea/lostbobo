from backend.core.kernel.command_bus import command_bus


@command_bus.handler("RL_STEP")
async def handle_rl_step(kernel, payload: dict):
    """Kernel-centered entrypoint for RL Service."""
    service = kernel.services["rl"]
    return await service.step(payload)
