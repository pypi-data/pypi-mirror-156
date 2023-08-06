from .transform import transform
from .dialects.younger_futhark.letters import get_letter_mapping
from .dialects.younger_futhark.runes import get_rune_mapping


def letters_to_runes(content: str) -> str:
    mapping = get_letter_mapping()
    return transform(content, mapping)


def runes_to_letters(content: str) -> str:
    mapping = get_rune_mapping()
    return transform(content, mapping)
