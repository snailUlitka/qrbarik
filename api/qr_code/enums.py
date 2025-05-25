from enum import Enum, auto

class Color(Enum):
    WHITE = auto()
    BLACK = auto()

    def __invert__(self):
        match self:
            case Color.WHITE:
                return Color.BLACK
            case Color.BLACK:
                return Color.WHITE
            
class Border(Enum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()