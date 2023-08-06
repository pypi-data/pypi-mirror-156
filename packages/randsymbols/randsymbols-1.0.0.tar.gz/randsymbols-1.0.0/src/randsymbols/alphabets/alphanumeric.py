from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Iterable
from enum import Enum


class Case(str, Enum):
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    MIXED = "mixed"


def get_alphabet(case: Case, enable_punctuation: bool) -> Iterable[str]:
    alphabet = (
        ascii_letters + digits
        if case is Case.MIXED
        else ascii_lowercase + digits
        if case is Case.LOWERCASE
        else ascii_uppercase + digits
        if case is Case.UPPERCASE
        else None
    )
    if enable_punctuation:
        alphabet += punctuation
    return alphabet
