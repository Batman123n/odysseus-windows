# src/constants.py
"""Application-wide constants and configuration values."""
import os
import sys
from pathlib import Path

APP_VERSION = "1.0.0"

# Base paths
# When compiled with Nuitka onefile, __file__ points to the temporary extraction directory.
# We want STATIC_DIR to point there (since assets are bundled), but DATA_DIR
# should point to the actual project root (next to the .exe).
IS_COMPILED = "__compiled__" in globals()

if IS_COMPILED:
    # Nuitka onefile sets NUITKA_ONEFILE_PARENT to the directory containing the .exe
    EXE_DIR = Path(os.environ.get("NUITKA_ONEFILE_PARENT", os.path.dirname(sys.executable)))
    # BASE_DIR inside the extracted bundle (where the code is)
    BUNDLE_DIR = Path(__file__).resolve().parent.parent
    
    BASE_DIR = str(BUNDLE_DIR) + "/"
    STATIC_DIR = BUNDLE_DIR / "static"
    DATA_DIR = EXE_DIR / "data"
else:
    BUNDLE_DIR = Path(__file__).resolve().parent.parent
    BASE_DIR = str(BUNDLE_DIR) + "/"
    STATIC_DIR = BUNDLE_DIR / "static"
    DATA_DIR = BUNDLE_DIR / "data"

# Ensure DATA_DIR is a string for legacy compatibility in this file's exports if needed, 
# but we want it as a Path object for modern usage.
# We'll keep it as a Path object.

# Data file paths
SESSIONS_FILE = str(DATA_DIR / "sessions.json")
MEMORY_FILE = str(DATA_DIR / "memory.json")
MEMORY_DOC = str(DATA_DIR / "memory_doc.md")
PERSONAL_DIR = str(DATA_DIR / "personal_docs")
RUNBOOK_DIR = str(Path(PERSONAL_DIR) / "runbook")
UPLOAD_DIR = str(DATA_DIR / "uploads")
FEATURES_FILE = str(DATA_DIR / "features.json")
SETTINGS_FILE = str(DATA_DIR / "settings.json")

# API Configuration
MAX_CONTEXT_MESSAGES = 90
REQUEST_TIMEOUT = 20
OPENAI_COMPAT_PATH = "/v1/chat/completions"

# Environment variables with defaults
DEFAULT_HOST = os.getenv("LLM_HOST", "localhost")
LLM_HOSTS = [h.strip() for h in os.getenv("LLM_HOSTS", "").split(",") if h.strip()]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEARXNG_INSTANCE = os.getenv('SEARXNG_INSTANCE', 'http://localhost:8080')


# Cleanup configuration
CLEANUP_ENABLED = os.getenv("CLEANUP_ENABLED", "True").lower() == "true"
CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))

# Default parameters
DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 0
