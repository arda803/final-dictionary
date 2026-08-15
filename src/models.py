"""Data models for the dictionary application."""
from typing import List, Dict, Any


class Translation:
    """A single translation/definition for an entry."""

    def __init__(self, part_of_speech: str = "", definition: str = "", example: str = ""):
        self.part_of_speech = part_of_speech
        self.definition = definition
        self.example = example

    def to_dict(self) -> Dict[str, str]:
        return {
            "part_of_speech": self.part_of_speech,
            "definition": self.definition,
            "example": self.example,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Translation":
        return cls(
            data.get("part_of_speech", ""),
            data.get("definition", ""),
            data.get("example", ""),
        )

    def __repr__(self) -> str:
        return f"Translation(pos={self.part_of_speech!r}, def={self.definition!r})"


class DictionaryEntry:
    """Represents a headword with its translations."""

    def __init__(
        self,
        word: str,
        language_pair: str,
        translations: List[Translation],
        status: str = "not_started",
        is_favorite: bool = False,
    ):
        self.word = word
        self.language_pair = language_pair
        self.translations = translations
        self.status = status
        self.is_favorite = is_favorite

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "language_pair": self.language_pair,
            "status": self.status,
            "is_favorite": self.is_favorite,
            "translations": [t.to_dict() for t in self.translations],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DictionaryEntry":
        translations = [Translation.from_dict(t) for t in data.get("translations", [])]
        return cls(
            data["word"],
            data["language_pair"],
            translations,
            data.get("status", "not_started"),
            data.get("is_favorite", False),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DictionaryEntry):
            return False
        return self.word == other.word and self.language_pair == other.language_pair

    def __hash__(self) -> int:
        return hash((self.word, self.language_pair))

    def __repr__(self) -> str:
        return f"DictionaryEntry({self.word!r}, {self.language_pair!r}, n_trans={len(self.translations)})"
