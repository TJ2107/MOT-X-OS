import subprocess


class ShellPlugin:
    def run_command(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            return exc.stderr.strip() or str(exc)
