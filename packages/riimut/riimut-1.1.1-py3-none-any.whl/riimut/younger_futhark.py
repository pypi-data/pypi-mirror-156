from enum import Enum
from .transform import _transform
from .dialects.younger_futhark.letters import (
    get_letters_to_long_branch_mapping,
    get_letters_to_short_twig_mapping,
)
from .dialects.younger_futhark.runes import get_rune_mapping


class Variant(str, Enum):
    LONG_BRANCH = ("long-branch",)
    SHORT_TWIG = "short-twig"


def letters_to_runes(content: str, variant: Variant = Variant.LONG_BRANCH) -> str:
    mapping = (
        get_letters_to_long_branch_mapping()
        if variant == Variant.LONG_BRANCH
        else get_letters_to_short_twig_mapping()
    )
    return _transform(content, mapping)


def letters_to_long_branch_runes(content: str) -> str:
    mapping = get_letters_to_long_branch_mapping()
    return _transform(content, mapping)


def letters_to_short_twig_runes(content: str) -> str:
    mapping = get_letters_to_short_twig_mapping()
    return _transform(content, mapping)


def runes_to_letters(content: str) -> str:
    mapping = get_rune_mapping()
    return _transform(content, mapping)
