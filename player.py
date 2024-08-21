from cards import Card

class Player:
    def __init__(self, name):
        self.hand = []
        self.name = name
    def find_card_with_code(self, code: str):
        for card in self.hand:
            if card.get_code() == code:
                return card  # Return early
        # If the code reaches here at all, that means no card is found.
        raise ValueError()
    def take_cards_by_code(self, card_codes: 'list[str]'):
        removed_cards = [] #type: list[Card] #Untuk kartu terbuang
        try:
            for code in card_codes: #Cek kode satu2
                card = self.find_card_with_code(code)
                self.hand.remove(card) #Kartu ketemu
                removed_cards.append(card)
        except ValueError:
            # Return the card already removed to hand.
            for card in removed_cards: #Balikin kartu kalau ga ketemu ke selfhand
                self.hand.append(card)
            # Re-raise error after hand is restored.
            raise ValueError('Some card is not found in the hand.')
        return removed_cards
    def add_card(self, card: 'Card'):
        self.hand.append(card)
    def add_cards(self, cards: list[Card]):
        for card in cards:
            self.hand.append(card)
    def announce(self, message):
        raise NotImplemented()
    def __str__(self) -> str:
        return self.name

