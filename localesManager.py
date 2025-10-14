import locale

availableLanguages = [
    "en_US",
    "it_IT",
    "es_ES",
    "fr_FR",
    "de_DE",
    "pt_PT",
    "zh_CN",
    "ja_JP",
    "ru_RU",
    "ko_KR",
]

def getCurrentLocale() -> str:
    lang = locale.getlocale()[0]
    if lang in availableLanguages:
        return lang
    else:
        return "en_US"

