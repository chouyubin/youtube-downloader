"""Windows no-console entry point for the Tkinter GUI."""
import multiprocessing
multiprocessing.freeze_support()
from pathlib import Path
import sys

APP_DIR = str(Path(__file__).resolve().parent)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from main import main


if __name__ == "__main__":
    main()
