from .transform import transform
from .dialects.futhorc.letters import get_letter_mapping
from .dialects.futhorc.runes import get_rune_mapping


def letters_to_runes(content: str) -> str:
    mapping = get_letter_mapping()
    return transform(content, mapping)


def runes_to_letters(content: str) -> str:
    mapping = get_rune_mapping()
    return transform(content, mapping)
