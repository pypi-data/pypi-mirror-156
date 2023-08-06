from typing import Final

MAPPING: Final = {
    "ᚠ": "f",
    "ᚢ": "u",
    "ᚦ": "þ",
    "ᚬ": "o",
    "ᚱ": "r",
    "ᚴ": "k",
    "ᚼ": "h",
    "ᚽ": "h",
    "ᚾ": "n",
    "ᚿ": "n",
    "ᛁ": "i",
    "ᛅ": "a",
    "ᛆ": "a",
    "ᛋ": "s",
    "ᛌ": "s",
    "ᛏ": "t",
    "ᛐ": "t",
    "ᛒ": "b",
    "ᛘ": "m",
    "ᛚ": "l",
    "ᛦ": "R",
    ":": " ",
}


def get_rune_mapping() -> dict[str, str]:

    return MAPPING
