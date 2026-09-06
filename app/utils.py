from rapidfuzz.fuzz import ratio


def normalize_word(word: str) -> str:
    return word.strip().lower()


def similarity(word1: str, word2: str) -> float:
    return ratio(
        normalize_word(word1),
        normalize_word(word2)
    ) / 100