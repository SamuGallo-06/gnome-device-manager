import translations
from localesManager import getCurrentLocale

class TranslationsProxy:
    def __init__(self):
        self.current_lang = getCurrentLocale()

    def __getattr__(self, name):
        """
        Restituisce automaticamente la traduzione nella lingua corrente.
        """
        if hasattr(translations, name):
            value_dict = getattr(translations, name)
            if isinstance(value_dict, dict):
                return value_dict.get(self.current_lang, list(value_dict.values())[0])
            return value_dict
        raise AttributeError(f"No translation found for '{name}'")

# Singleton da importare
tr = TranslationsProxy()