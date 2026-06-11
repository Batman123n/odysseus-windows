import uvicorn
import os
import multiprocessing
from app import app

if __name__ == "__main__":
    # Nuitka might need this for some multiprocessing-related packages
    multiprocessing.freeze_support()
    
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "127.0.0.1")
    
    print(f"Starting Odysseus Backend on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
