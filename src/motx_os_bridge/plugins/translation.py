import re


class TranslationPlugin:
    def translate_to_french(self, text: str) -> str:
        if not text:
            return "❌ Aucun texte à traduire"

        try:
            import importlib
            googletrans = importlib.import_module("googletrans")
            Translator = getattr(googletrans, "Translator")
            translator = Translator()
            translated = translator.translate(text, src="en", dest="fr")
            return f"✅ Traduction : {translated.text}"
        except ImportError:
            return self._fallback_translate(text)
        except Exception:
            return self._fallback_translate(text)

    def _fallback_translate(self, text: str) -> str:
        dictionary = {
            "hello": "bonjour",
            "goodbye": "au revoir",
            "please": "s'il vous plaît",
            "thank": "merci",
            "thanks": "merci",
            "yes": "oui",
            "no": "non",
            "note": "note",
            "take": "prendre",
            "open": "ouvrir",
            "file": "fichier",
            "folder": "dossier",
            "search": "rechercher",
            "computer": "ordinateur",
            "system": "système",
            "error": "erreur",
            "success": "succès",
            "run": "exécuter",
            "translate": "traduire",
            "language": "langue",
            "english": "anglais",
            "french": "français"
        }

        def translate_word(word: str) -> str:
            lower = word.lower()
            punctuation = re.sub(r"[A-Za-z0-9]", "", word)
            translated = dictionary.get(lower, word)
            if word[0].isupper():
                translated = translated.capitalize()
            return translated + punctuation

        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        translated_tokens = [translate_word(token) if re.match(r"\w+", token) else token for token in tokens]
        return "✅ Traduction approximative : " + "".join(translated_tokens)
