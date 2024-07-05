def LanguageCode(lang):
    codelang = {
        'batak toba' : 'bbc',
        'jepang' : 'ja',
        'indonesia' : 'id',
    }

    lang_lower = lang.lower()
    if 'bahasa' in lang_lower:
        lang_lower = lang_lower.replace('bahasa','').strip()

    if lang_lower in codelang:
        return codelang[lang_lower]
    else:
        return 'unknown'
