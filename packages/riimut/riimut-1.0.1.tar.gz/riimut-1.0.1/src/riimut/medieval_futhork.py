from .transform import transform
from .dialects.medieval_futhork.letters import get_letter_mapping
from .dialects.medieval_futhork.runes import get_rune_mapping


def letters_to_runes(content: str) -> str:
    mapping = get_letter_mapping()
    return transform(content, mapping)


def runes_to_letters(content: str) -> str:
    mapping = get_rune_mapping()
    return transform(content, mapping)
