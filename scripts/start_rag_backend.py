import subprocess
import socket
import os
import sys
import time

RAG_BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Astra - Universal RAG/backend/main.py'))
RAG_PORT = 8000
AUTO_INGEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'auto_ingest.py'))
DEFAULT_DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'astratrade_app/docs'))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_rag_backend():
    if is_port_in_use(RAG_PORT):
        print(f"Universal RAG backend is already running on port {RAG_PORT}.")
        return True
    try:
        # Start the backend as a background process
        process = subprocess.Popen([sys.executable, RAG_BACKEND_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Started Universal RAG backend on port {RAG_PORT}. Waiting for it to become available...")
        # Wait for the port to be open (max 20 seconds)
        for _ in range(40):
            if is_port_in_use(RAG_PORT):
                print("Backend is now running.")
                return True
            time.sleep(0.5)
        print("Backend did not start within the expected time.")
        return False
    except Exception as e:
        print(f"Error starting Universal RAG backend: {e}")
        return False

def run_auto_ingest(docs_dir=DEFAULT_DOCS_DIR):
    try:
        print(f"Running auto_ingest.py to ingest docs from {docs_dir} ...")
        subprocess.run([sys.executable, AUTO_INGEST_PATH, docs_dir], check=True)
    except Exception as e:
        print(f"Error running auto_ingest.py: {e}")

if __name__ == "__main__":
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DOCS_DIR
    if start_rag_backend():
        run_auto_ingest(docs_dir)