# conftest.py (racine du repo)
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
# S'assurer que la racine du repo est dans le PYTHONPATH
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
