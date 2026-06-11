"""
chroma_client.py

Singleton ChromaDB HTTP client.
Connects to a ChromaDB instance running as a standalone service.
"""

import os
import socket
import logging

logger = logging.getLogger(__name__)

_client = None

# A short connect probe so an unreachable ChromaDB fails fast instead of
# blocking on the OS connection timeout (~30-60s, WinError 10060 on Windows),
# which otherwise stalls app startup. Tunable via CHROMADB_CONNECT_TIMEOUT.
_CONNECT_TIMEOUT = float(os.getenv("CHROMADB_CONNECT_TIMEOUT", "2.0"))


def _port_open(host: str, port: int, timeout: float = None) -> bool:
    """Return True if a TCP connection to host:port succeeds within timeout."""
    try:
        with socket.create_connection((host, port), timeout=timeout or _CONNECT_TIMEOUT):
            return True
    except OSError:
        return False


def get_chroma_client():
    """Get or create the singleton ChromaDB client.

    Tries an HTTP client first (standalone service, e.g. Docker). If the service
    is unreachable, it falls back to a PersistentClient (embedded mode) using
    `data/chroma` for storage. This allows the app to run natively without
    requiring Docker / WSL.
    """
    global _client
    if _client is not None:
        return _client

    try:
        import chromadb
    except ImportError as e:
        raise RuntimeError(
            "ChromaDB integration is not installed. Install the optional "
            "dependency with: pip install chromadb"
        ) from e

    host = os.getenv("CHROMADB_HOST", "localhost")
    port = int(os.getenv("CHROMADB_PORT", "8100"))

    # 1. Try HTTP client if the port is open
    if _port_open(host, port):
        try:
            client = chromadb.HttpClient(host=host, port=port)
            client.heartbeat()
            _client = client
            logger.info(f"ChromaDB connected (HTTP): {host}:{port}")
            return _client
        except Exception as e:
            logger.warning(f"ChromaDB HTTP connection failed even though port is open: {e}")

    # 2. Fall back to PersistentClient (embedded)
    try:
        persist_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "chroma"
        )
        os.makedirs(persist_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=persist_dir)
        client.heartbeat()
        _client = client
        logger.info(f"ChromaDB initialized (Persistent): {persist_dir}")
        return _client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize ChromaDB (HTTP and Persistent both failed): {e}") from e


def reset_client():
    """Reset the singleton (e.g. after config change)."""
    global _client
    _client = None
