from app.core.telemetry import emit


DAG = {
    "boot": [],
    "init": ["boot"],
    "load": ["init"],
    "execute": ["load"],
}


def run_ci_dag():
    run_dag(mode="ci")


def run_worker_dag():
    run_dag(mode="worker")


def run_dev_dag():
    run_dag(mode="dev")


def run_dag(mode: str):
    completed = set()

    def can_run(node):
        return all(dep in completed for dep in DAG[node])

    while len(completed) < len(DAG):
        for node in DAG:
            if node not in completed and can_run(node):
                emit("NODE_START", node=node, mode=mode)

                # placeholder execution
                emit("NODE_DONE", node=node, mode=mode)

                completed.add(node)
