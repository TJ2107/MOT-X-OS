import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class CommunicationPlugin:
    def send_email(self, to: str, subject: str, body: str, sender: Optional[str] = None, password: Optional[str] = None) -> str:
        """Send email via SMTP (requires config)"""
        try:
            if not sender or not password:
                return "⚠️ Configuration email manquante (sender/password)"

            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.send_message(msg)
            return f"✅ Email envoyé à : {to}"
        except Exception as e:
            return f"❌ Erreur email : {e}"

    def send_notification(self, title: str, message: str) -> str:
        """Send Windows notification"""
        try:
            import subprocess
            cmd = f'powershell -Command "Add-Type –AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'{message}\', \'{title}\')"'
            subprocess.run(cmd, shell=True)
            return f"✅ Notification enviée : {title}"
        except Exception as e:
            return f"❌ Erreur notification : {e}"

    def play_sound(self, sound_type: str = "default") -> str:
        """Play system sound"""
        try:
            import winsound
            # winsound constants for different sound types
            sound_map = {
                "info": 1000,      # frequency
                "warning": 500,
                "error": 200,
                "default": 1000
            }
            frequency = sound_map.get(sound_type, 1000)
            winsound.Beep(frequency, 500)  # frequency in Hz, duration in ms
            return f"✅ Son joué : {sound_type}"
        except Exception as e:
            return f"❌ Erreur son : {e}"


