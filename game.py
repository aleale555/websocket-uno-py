from cards import generate_cards, Action, Color
from random import shuffle, seed
import re
TYPE_CHECK = False
if TYPE_CHECK:
    from player import Player
    from cards import Card
class Deck:
    def __init__ (self):
        self.draw_pile = generate_cards()
        self.discard_pile = [] #type: list[Card]
        shuffle(self.draw_pile)
        self.announced_color = None
    def draw(self):
        if len(self.draw_pile) == 0: #Empty Pile of Cards
            shuffle(self.discard_pile)
            #Reshuffle
            self.draw_pile = self.discard_pile
            #Make new pile
            self.discard_pile = []
            #now the discard pile is empty
        return self.draw_pile.pop()
    def discard(self, cards):
        for card in cards:
            self.discard_pile.append(card)
    def get_last_card(self):
        return self.discard_pile[-1]
    def draw_many(self, num):
        out = []
        for _ in range(num):
            out.append(self.draw())
        return out
    
class GameController:
    def __init__(self, players: 'list[Player]') -> None:
        self.players = players
        self.turn = 0
        self.turn_direction = 1 #Clockwise 1 Counterclockwise -1
        self.deck = Deck()
        self.plus_stack = 0 #Catat seberapa banyak plus yang ditumpuk
        self.announce_color = None
    async def start_game(self):
        await self.announce_all('The game has started.')
        for player in self.players:
            player.add_cards(self.deck.draw_many(7)) #7 Kartu awal di tangan
            await player.announce(f"Your deck is {' '.join(map(str, player.hand))}")
        await self.announce_all(f"It's {self.get_current_player()}'s turn.")
        first_card = self.deck.draw()
        self.deck.discard([first_card])
        await self.announce_all(f"It's a {first_card}")
        if first_card.type == Action.Reverse:
            self.turn_direction = -1
        elif first_card.type == Action.Skip:
            self.turn += 1
            await self.announce_all (f"Skipped, now it's {self.get_current_player}'s turn")
        elif first_card.type == Action.Plus2:
            self.plus_stack += 2
        elif first_card.type == Action.Plus4:
            self.plus_stack += 4
        await self.get_current_player().announce('*')
        
    async def announce_new_turn(self):
        await self.announce_all(f"The top of the pile is now {self.deck.get_last_card()}.")
        self.advance_turn()   #Pindah ke next player
        await self.announce_all(f"It's {self.get_current_player()}'s turn. ".ljust(20, '='))
        await self.get_current_player().announce(f'Your hand is {" ".join(map(str, self.get_current_player().hand))}')
        await self.get_current_player().announce('*') #* Pesan utk nandain client gilirannya

    async def on_player_input(self, player: 'Player', message: str): #Untuk draw kartu
        #Pengirim pesan bukan current player
        if player != self.get_current_player():
            return
        #Jika pesan isinya draw
        if message == 'draw':
            if self.plus_stack > 0:
                cards = []
                for _ in range(self.plus_stack):
                    cards.append(self.deck.draw())
                    player.add_cards(cards)
                await self.announce_all(f"{player} drew {[self.plus_stack]} cards. ")
                await player.announce(f'You drew {" ".join(map(str, cards))}')
                self.plus_stack = 0
            else:
                drawn_card = self.deck.draw()
                player.add_card(drawn_card)
                await self.announce_all(f'{player} drew a card.')
                await player.announce(f'You drew a {drawn_card}')
            await player.announce(f'Your hand is {" ".join(map(str, player.hand))}')
            await self.announce_new_turn()
            return
        try:
            first_card, cards, announced_color, uno = self.parse_and_validate(message, player)
        except ValidationFailed as e:
            await player.announce(str(e))
            await player.announce('*')
            return

        await self.announce_all(f'{player} played {', '.join(map(str, cards))}') 
        #Map manggil fungsi pertama ke masing2 elemen yang ada di arg 2 di cards
        if first_card.type == Action.Plus2:
            self.plus_stack += len(cards) * 2
        if first_card.type == Action.Plus4:
            self.plus_stack += len(cards) * 4
        if first_card.type == Action.Reverse:
            if len(cards) % 2 != 0:
                self.turn_direction *= -1
        if len(player.hand) == 0:
            await self.announce_all(f'{player} won the game!')
            del self.players[self.turn]
            if len(self.players) == 1:
                await self.announce_all(
                    f'All player has won except of {self.players[0]}',
                    'The game is over',
                    '$')
                return
            if self.turn_direction < 0:
                pass  # The turn doesn't change
            else:
                self.turn = (self.turn - 1) % len(self.players)        
        if first_card.type == Action.Skip:
            self.advance_turn(len(cards)) #len(cards) banyaknya skip dibuang
        
        self.announce_color = announced_color
        self.deck.discard(cards)
        await self.announce_new_turn()

    def parse_and_validate(self, message, player):
        try:
            card_codes, announced_color, uno = self.breakdown_message(message)
            cards = player.take_cards_by_code(card_codes)
        except SyntaxError:
            raise ValidationFailed('[ERR] Wrong format. Try again.')
        except ValueError:
            raise ValidationFailed("[ERR] Some cards are not found in the hand.")
        #Cek kartunya tipenya sama
        first_card = cards[0]
        for card in cards:
            if card.type != first_card.type:
                player.add_cards(cards)
                raise ValidationFailed('[ERR] All cards must be the same type.')
            #Cek kartunya counteringnya valid
        if not first_card.can_play_over(self.deck.get_last_card(), self.announce_color, self.plus_stack > 0):
                player.add_cards(cards) #Kembalikan kartu yang sudah diambil

                raise ValidationFailed(f"[ERR] {first_card} cannot play over the last card.")
        if (first_card.type == Action.Plus4 or first_card.type == Action.Wild) and announced_color is None:
            player.add_cards(cards)
            raise ValidationFailed(f'[ERR] Playing a wild or +4 should announce the color')
        return first_card, cards, announced_color, uno

    def get_current_player(self):
        return self.players[self.turn]
    def advance_turn(self, turns= 1):
        self.turn = (self.turn + self.turn_direction * turns) % len(self.players)  #Pindah ke next player
    async def announce_all(self, *messages):
        for player in self.players:
            for message in messages:
                await player.announce(message)
    def breakdown_message(self, message: str):
        format = re.compile(
            r'(?P<played_cards>(([0-9srt][RGBY])|[wf])( (([0-9srt][RGBY])|[wf]))*)'
            + r'( (?P<announced_color>[RGBY]))?'
            + r'( (?P<uno>uno))?'
            + '$'
        )
        match = format.match(message)
        if match is None:
            raise SyntaxError()
        card_codes_raw = match['played_cards']
        announced_color_str = match['announced_color']
        uno_str = match['uno']

        card_codes = card_codes_raw.split(' ')
        if announced_color_str == 'R':
            announced_color = Color.Red
        elif announced_color_str == 'G':
            announced_color = Color.Green
        elif announced_color_str == 'B':
            announced_color = Color.Blue
        elif announced_color_str == 'Y':
            announced_color = Color.Yellow
        else:
            announced_color = None

        uno = uno_str is not None
        return (card_codes, announced_color, uno)

class ValidationFailed(Exception):
    pass
seed(0)