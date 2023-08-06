import emojis
from typing import Iterable
from enum import Enum


class EmojiCategory(str, Enum):
    ANY = "Any"
    NATURE = "Animals & Nature"
    PEOPLE = "People & Body"
    FOOD = "Food & Drink"
    SYMBOLS = "Symbols"
    FLAGS = "Flags"
    PLACES = "Travel & Places"
    EMOTION = "Smileys & Emotion"
    ACTIVITIES = "Activities"
    OBJECTS = "Objects"


def get_alphabet(category: EmojiCategory) -> Iterable[str]:
    return (
        list(emojis.db.get_emoji_aliases().values())
        if category is EmojiCategory.ANY
        else list(e.emoji for e in emojis.db.get_emojis_by_category(category.value))
    )
