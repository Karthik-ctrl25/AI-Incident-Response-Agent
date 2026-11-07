"""AI Incident Response Agent - Backend Application Package."""
import sys
from pathlib import Path

# Automatically ensure 'backend' directory is in sys.path so 'app' is resolvable
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
