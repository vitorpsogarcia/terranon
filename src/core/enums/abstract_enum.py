from enum import Enum


class AbstractEnum(Enum):

    @staticmethod
    def get_by_text(text: str):
        for enum in AbstractEnum.__members__.values():
            if enum.value == text:
                return enum
        return None