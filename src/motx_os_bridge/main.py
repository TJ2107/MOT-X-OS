import asyncio
import threading
import time
from motx_os_bridge.core.engine import MOTXAutomationEngine
from motx_os_bridge.core.cognitive_layer import CognitiveOperatingLayer
from motx_os_bridge.utils.config_loader import load_settings

def start_fastapi_server(host, port):
    import uvicorn
    from motx_os_bridge.api.server_v2 import app
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)

    def _run():
        server.run()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    timeout = time.time() + 10
    while time.time() < timeout:
        if server.started:
            print(f"🔌 FastAPI server démarré en arrière-plan sur http://{host}:{port}")
            return
        if not thread.is_alive():
            break
        time.sleep(0.1)

    raise RuntimeError(f"FastAPI server failed to start on http://{host}:{port}. Check logs for errors.")

async def main():
    engine = MOTXAutomationEngine(interactive=True)
    settings = load_settings()
    api_settings = settings.get("api", {}) if isinstance(settings, dict) else {}
    if api_settings.get("enabled"):
        host = api_settings.get("host", "127.0.0.1")
        port = api_settings.get("port", 8000)
        start_fastapi_server(host, port)

    print("=" * 60)
    print("MOT-X OS - Cognitive Operating Layer v0.2")
    print("=" * 60)
    print("Tapez 'cognitive <instruction>' pour mode cognitif")
    print("Tapez 'exit' ou 'quit' pour terminer\n")

    col = CognitiveOperatingLayer()

    while True:
        try:
            instruction = input("📝 MOT-X > ").strip()

            if not instruction:
                continue

            if instruction.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Au revoir!")
                break

            # Mode cognitif
            if instruction.lower().startswith("cognitive "):
                cognitive_instruction = instruction[10:].strip()
                if cognitive_instruction:
                    result = await col.execute_cognitive_cycle(cognitive_instruction)
                    print(f"\n🎯 Cycle complet exécuté. Tâches exécutées: {result['results']['tasks_executed']}\n")
                continue

            # Mode classique
            results = await engine.process_instruction(instruction)

            print("\n✅ Résultats :")
            for index, result in enumerate(results, start=1):
                print(f"   {index}. {result}")
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Arrêt par l'utilisateur")
            break


def run():
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        print(f"\n❌ Erreur : {e}\n")


if __name__ == "__main__":
    run()
