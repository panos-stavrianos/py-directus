from typing import Optional


def parse_translations(all_translations: list[dict]) -> dict[str, dict[str, str]] | None:
    if all_translations is None or not all_translations:
        return None

    return {
        translations['key']: {
            translation['languages_code']: translation['translation']
            for translation in translations['translations']
        } for translations in all_translations
    }
