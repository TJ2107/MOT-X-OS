import psutil
import platform
import os


class SystemInfoPlugin:
    def get_system_info(self) -> str:
        try:
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu_percent = psutil.cpu_percent(interval=1)

            return f"""✅ Informations système :
  - OS: {platform.system()} {platform.release()}
  - CPU: {cpu_percent}%
  - RAM: {ram.percent}% ({ram.used // (1024**3)}GB/{ram.total // (1024**3)}GB)
  - Disque: {disk.percent}% ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)"""
        except Exception as e:
            return f"❌ Erreur info système : {e}"

    def restart_pc(self, delay: int = 60) -> str:
        import subprocess
        try:
            if platform.system() == "Windows":
                subprocess.run(f"shutdown /r /t {delay}", shell=True)
                return f"✅ Redémarrage programmé dans {delay} secondes"
            else:
                subprocess.run(f"shutdown -r +{delay//60}", shell=True)
                return f"✅ Redémarrage programmé"
        except Exception as e:
            return f"❌ Erreur redémarrage : {e}"

    def shutdown_pc(self, delay: int = 60) -> str:
        import subprocess
        try:
            if platform.system() == "Windows":
                subprocess.run(f"shutdown /s /t {delay}", shell=True)
                return f"✅ Arrêt programmé dans {delay} secondes"
            else:
                subprocess.run(f"shutdown -h +{delay//60}", shell=True)
                return f"✅ Arrêt programmé"
        except Exception as e:
            return f"❌ Erreur arrêt : {e}"
