from datetime import date
from typing import Optional, Tuple

GENERATIONS = {
    "gen_alpha":   {"label": "Gen Alpha",   "birth_start": 2013, "birth_end": 2025},
    "gen_z":       {"label": "Gen Z",       "birth_start": 1997, "birth_end": 2012},
    "millennial":  {"label": "Millennials", "birth_start": 1981, "birth_end": 1996},
    "gen_x":       {"label": "Gen X",       "birth_start": 1965, "birth_end": 1980},
    "boomer":      {"label": "Boomers",     "birth_start": 1946, "birth_end": 1964},
}

BORDER_YEARS = {1996, 1997}


def _current_year() -> int:
    return date.today().year


def get_age_range(key: str) -> Optional[Tuple[int, int]]:
    gen = GENERATIONS.get(key)
    if not gen:
        return None
    year = _current_year()
    age_min = year - gen["birth_end"]
    age_max = year - gen["birth_start"]
    return (age_min, age_max)


def resolve_generation_age_range(name: str) -> Optional[Tuple[int, int]]:
    lower = name.lower()
    if "alpha" in lower:
        return get_age_range("gen_alpha")
    if "boomer" in lower:
        return get_age_range("boomer")
    if "millennial" in lower:
        return get_age_range("millennial")
    if "generation x" in lower or "gen x" in lower:
        return get_age_range("gen_x")
    if "generation z" in lower or "gen z" in lower:
        return get_age_range("gen_z")
    return None
