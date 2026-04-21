# run_dashboard.py
import os
import subprocess
import sys

os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

script_dir = os.path.dirname(os.path.abspath(__file__))

sys.exit(subprocess.call([
    sys.executable, "-m", "streamlit", "run",
    os.path.join(script_dir, "dashboard.py")
], cwd=script_dir))