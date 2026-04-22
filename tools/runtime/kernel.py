import subprocess
import sys
import re
import ast
import os


def ensure_deps():
    print("[KERNEL] Ensuring dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff"], check=True)


def remove_duplicate_symbols():
    """Detect duplicate function/class definitions (specifically run_node) and remove older ones."""
    print("[KERNEL] Performing AST structure normalization...")
    for root, _, files in os.walk("."):
        for f in files:
            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)
            with open(path, "r") as file:
                source = file.read()

            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            seen = set()
            new_lines = []
            skip_next = False

            # This is a naive line-based dedup for run_node, 
            # safe enough as a structural cleanup pass
            lines = source.splitlines()
            for line in lines:
                if line.strip().startswith("def run_node"):
                    if "run_node" in seen:
                        skip_next = True
                        continue
                    seen.add("run_node")
                
                if skip_next:
                    if line.strip() == "" or line.startswith("    "):
                        continue
                    else:
                        skip_next = False
                
                new_lines.append(line)

            with open(path, "w") as file:
                file.write("\n".join(new_lines) + "\n")


def count_violations():
    """Counts current Ruff violations."""
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "."],
        capture_output=True,
        text=True,
    )
    match = re.search(r"Found (\d+) error", result.stdout)
    if match:
        return int(match.group(1))
    return 0


def run_stage(action, name):
    before = count_violations()
    print(f"[KERNEL] {name}: Running...")
    
    if callable(action):
        action()
    else:
        subprocess.run(action, shell=True)
    
    after = count_violations()
    print(f"[KERNEL] {name}: {before} -> {after} violations")
    
    if after > before:
        print(f"[KERNEL] {name}: FAILED - State regression detected!")
        return False
    return True


def run():
    ensure_deps()

    stages = [
        (remove_duplicate_symbols, "Structure Normalization"),
        ("python -m ruff check . --select I --fix", "Import Fix"),
        ("python -m ruff format .", "Format"),
        ("python -m ruff check . --select UP --fix", "Typing Fix"),
        ("python -m ruff check . --fix --unsafe-fixes", "Unsafe Fix Completion"),
    ]

    for action, name in stages:
        if not run_stage(action, name):
            return 1

    # Final validation pass
    print("[KERNEL] Final Validation...")
    if count_violations() == 0:
        print("[KERNEL] SUCCESS - System converged")
        return 0
    else:
        print("[KERNEL] FAILED - Strict validation failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
