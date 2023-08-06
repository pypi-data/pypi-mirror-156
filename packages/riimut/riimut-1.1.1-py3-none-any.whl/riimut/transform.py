def _transform(content: str, mapping: dict[str, str]) -> str:
    return "".join([mapping.get(letter.lower(), letter) for letter in content])
