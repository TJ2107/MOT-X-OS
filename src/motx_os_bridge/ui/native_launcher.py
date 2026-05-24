import webview
import time
import urllib.request
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("native_launcher")

def wait_for_frontend(url="http://localhost:5173", timeout=30):
    logger.info(f"⏳ Waiting for frontend at {url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Tenter d'ouvrir l'URL
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    logger.info("✅ Frontend is ready!")
                    return True
        except Exception:
            time.sleep(1)
    logger.error("❌ Timeout waiting for frontend.")
    return False

def main():
    frontend_url = "http://localhost:5173"
    
    # Attendre que le frontend soit lancé
    if not wait_for_frontend(frontend_url):
        logger.error("Frontend not ready, launching browser fallback instead...")
        sys.exit(1)
        
    logger.info("🚀 Launching native window...")
    
    # Créer une fenêtre native borderless (sans bordure) déplaçable
    window = webview.create_window(
        title="MOT-X OS",
        url=frontend_url,
        width=1180,
        height=780,
        resizable=True,
        frameless=True,       # Borderless, pas de cadre standard OS
        easy_drag=True,       # Déplacement de la fenêtre en cliquant n'importe où
        background_color="#0F0F1A" # Couleur sombre premium pour éviter le flash blanc au chargement
    )
    
    # Démarrer le moteur de rendu WebView2 (Edge Chromium sous Windows)
    webview.start(gui="edgehtml" if sys.platform == "win32" else None)

if __name__ == "__main__":
    main()
