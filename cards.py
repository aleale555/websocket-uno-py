from enum import Enum
class Card:
    def __init__(self, color, type):
        self.color = color
        self.type = type
        self.countering_type = type
        if type == Action.Plus2 or type == Action.Plus4:
            self.countering_type = 'plus'
    def __str__(self) -> str:
        terminal_color_code = {
            None: 97,
            Color.Red: 91,
            Color.Green: 92,
            Color.Blue: 94,
            Color.Yellow: 93
        }[self.color]
        return f'\033[{terminal_color_code}m{self.get_code()}\033[0m'
    def get_code(self):
        if self.color is None:      #The Card= Wild or +4
            color_string = ''
        else:                       #R,G,B,Y
            color_string = self.color.value
        if isinstance(self.type, int):#0~9 in Color
            type_string = str(self.type)
        else:                       #srtwp in Color
            type_string = self.type.value
        return type_string + color_string
    def __repr__(self) -> str:
        return f'<Card {self}>'
    def is_wild(self):
        return self.type == Action.Plus4 or self.type == Action.Wild
    def can_play_over(self, last_played, announced_color):
        if last_played.is_wild():
            last_played_color = announced_color
        else:
            last_played_color = last_played.color
        return (
            self.is_wild() or
            (last_played_color == self.color) or
            (self.countering_type == last_played.countering_type)
        )
def normalize_plus_type(type):
    if type == Action.Plus2 or type == Action.Plus4:
        return 'plus'
    return type
class Action(Enum):
    Skip = 's'
    Reverse = 'r'
    Plus2 = 't'
    Wild = 'w'
    Plus4 = 'f'
class Color(Enum):
    Red = 'R'
    Green = "G"
    Blue = "B"
    Yellow = "Y"
class InvalidCardCombinationError(Exception):
    pass
def generate_cards():
    out = [] #type: list[Card]
    for col in Color:
        out.append(Card(None,Action.Wild))
        out.append(Card(None,Action.Plus4))
        out.append(Card(col, 0)) #No0 in 4 colors
        for num in range(9):
            out.append(Card(col, num + 1))
            out.append(Card(col, num + 1))
        for action in [Action.Plus2, Action.Skip, Action.Reverse]:
            out.append(Card(col, action))
            out.append(Card(col, action))
    return out





#- nR = number of red
#- rR = reverse of red
#- sR = skip of red
#- tR = plus two of red
#- w = wild
#- f = plus four

#to ASK
#   return, break, is when exactly
