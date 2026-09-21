import sys
import os

def get_project_root():
    if "NEXUS_ROOT" in os.environ and os.path.exists(os.environ["NEXUS_ROOT"]):
        return os.path.abspath(os.environ["NEXUS_ROOT"])
    cur = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    for _ in range(5):
        if os.path.exists(os.path.join(cur, "requirements.txt")) and (
            os.path.exists(os.path.join(cur, "src")) or os.path.exists(os.path.join(cur, "data"))
        ):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return cur

ROOT_DIR = get_project_root()
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Execute the main dashboard with isolated scope and exact file path
dashboard_file = os.path.join(ROOT_DIR, "src", "dashboards", "app.py")
with open(dashboard_file, "r", encoding="utf-8") as f:
    code = compile(f.read(), dashboard_file, 'exec')
    exec(code, {**globals(), "__file__": dashboard_file})
