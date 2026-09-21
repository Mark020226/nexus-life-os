import sys
import os

# Set root directory in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Execute the main dashboard
dashboard_file = os.path.join(ROOT_DIR, "src", "dashboards", "app.py")
with open(dashboard_file, "r", encoding="utf-8") as f:
    code = compile(f.read(), dashboard_file, 'exec')
    exec(code, globals())
