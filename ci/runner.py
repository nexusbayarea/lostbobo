import yaml
import subprocess


def run_step(step):
    print(f"Running: {step['run']}")
    result = subprocess.run(step["run"], shell=True)
    if result.returncode != 0:
        raise SystemExit(f"Step failed: {step['run']}")


def main():
    with open("ci/workflow.yml", "r") as f:
        wf = yaml.safe_load(f)

    steps = wf["steps"]
    edges = wf.get("edges", {})

    executed = set()

    def run_node(node):
        if node in executed:
            return

        step = steps[node]

        if step["type"] == "command":
            run_step(step)

        elif step["type"] == "parallel":
            for sub in step["runs"]:
                run_node(sub)

        executed.add(node)

        if node in edges:
            run_node(edges[node])

    entry = wf["entry"]
    run_node(entry)


if __name__ == "__main__":
    main()
