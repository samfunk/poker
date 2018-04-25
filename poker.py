from functools import reduce
from itertools import combinations
import random

class Card(object):
    def __init__(self, rank, value, suit):
        self.rank = rank
        self.value = value
        self.suit = suit
        self.card = str(self.value) + " of " + str(self.suit)
    def __eq__(self, other):
        return self.rank == other.rank and self.value == other.value and self.suit == other.suit

class Deck(object):
    def __init__(self):
        self.shuffle()

    def __len__(self):
        return len(self.deck)

    def populateDeck(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        for suit in suits:
            for rank in range(2,15):
                if rank == 11:
                    value = 'Jack'
                elif rank == 12:
                    value = 'Queen'
                elif rank == 13:
                    value = 'King'
                elif rank == 14:
                    value = 'Ace'
                else:
                    value = str(rank)
                self.deck.append(Card(rank, value, suit))

    def shuffle(self):
        self.deck = []
        self.populateDeck()
        random.shuffle(self.deck)

    def deal(self):
        card = self.deck.pop()
        return card

class Player(object):
    def __init__(self, name, stack):
        self.name = name
        self.stack = stack
        self.reset()

    def raises(self, amount):
        self.stack -= amount
        self.street_bet += amount
        self.pot_bet += amount
        self.is_checked = True

    def fold(self):
        self.reset()
        self.is_in = False  # Reset makes is_in True

    def reset(self):
        self.street_bet = 0
        self.pot_bet = 0

        self.hole_cards = []
        self.hand_score = 0
        self.hand_string = None
        self.best_hand = []
        self.high_card = []

        self.is_in = True
        self.is_checked = False

class Hand:

    def __init__(self, *players):
        self.total_pot = 0
        self.high_street_bet = 0
        self.deck = Deck()
        self.board = []
        self.player_list = []
        self.winner = None
        for player in players:
            self.player_list.append(player)

    def __len__(self):
        return len([player for player in self.player_list if player.is_in])

    def actions(self):

        # If someone raises, make all other players unchecked
        def reset_checks(new_leader, remaining_players):
            for player in remaining_players:
                if player != new_leader:
                    player.is_checked = False

        # Reset the street bet and players' street bets to 0
        self.high_street_bet = 0
        for player in self.player_list:
            player.is_checked = False
            player.street_bet = 0

        # While there at least two players and not all players are checked, allow players to make actions (bet/fold/call/check)
        while self.__len__() > 1 and False in [player.is_checked for player in self.player_list if player.is_in]:
            print('\nMax street bet: $' + str(self.high_street_bet))
            for player in [player for player in self.player_list if player.is_in]:

                while True:
                    action = str(input('{} (Amount to Call: ${} | Pot Bet: ${} | Stack: ${}) Action: '.format(player.name, self.high_street_bet - player.street_bet, player.pot_bet, player.stack))).strip().lower()
                    if action not in ['raise', 'call', 'check', 'fold']:
                        print('Must be a valid action!')
                        continue

                    elif action == 'raise':
                        if player.stack == 0:
                            print('You don\'t have enough chips!')
                            continue
                        else:
                            while True:
                                try:
                                    amount = int(input('Amount: '))
                                except ValueError:
                                    print('Must be a valid integer!')
                                    continue

                                if amount > player.stack:
                                    print('You don\'t have enough')
                                    continue

                                elif amount < self.high_street_bet - player.street_bet:
                                    print('You must raise more than current high street bet')
                                    continue

                                elif amount == self.high_street_bet - player.street_bet:
                                    print('Call instead of Raise next time!')
                                    break

                                else:
                                    break

                            player.raises(amount)
                            self.total_pot += amount
                            reset_checks(player, self.player_list)

                            if player.street_bet > self.high_street_bet:
                                self.high_street_bet = player.street_bet

                            break

                    elif action == 'call':
                        if player.stack == 0:
                            print('You don\'t have enough chips')
                            continue
                        elif player.street_bet == self.high_street_bet:
                            print('You are the bet leader, Check!')
                            continue
                        else:
                            amount = self.high_street_bet - player.street_bet
                            if amount > player.stack:
                                amount = player.stack
                            player.raises(amount)
                            self.total_pot += amount
                            break

                    elif action == 'check':
                        if player.street_bet < self.high_street_bet:
                            print('You must Call or Raise!')
                            continue
                        else:
                            player.is_checked = True
                            break

                    elif action == 'fold':
                        player.fold()
                        break

    def deal_cards(self):
        for _ in range(2):
            for player in self.player_list:
                player.hole_cards.append(self.deck.deal())

    def flop(self):
        self.high_street_bet = 0
        self.deck.deal()
        for _ in range(3):
            self.board.append(self.deck.deal())

    def turn(self):
        self.high_street_bet = 0
        self.deck.deal()
        self.board.append(self.deck.deal())

    def river(self):
        self.high_street_bet = 0
        self.deck.deal()
        self.board.append(self.deck.deal())

    def evaluate_hand(self, hand):
        values, suits = [list(x) for x in zip(*sorted(hand))]

        moder = lambda x: max(set(x), key=x.count)

        if [10,11,12,13,14] == values:
            # Royal Flush
            if len(set(suits)) == 1:
                return 10, [14], 'Royal Flush'
            # (Royal) Straight
            else:
                return 5, [14], 'Straight'

        elif [2,3,4,5,14] == values:
            # (Low) Straight Flush
            if len(set(suits)) == 1:
                return 9, [5], 'Straight Flush'
            # (Low) Straight
            else:
                return 5, [5], 'Straight'

        elif len(set(values)) == 5 and values[-1] - values[0] == 4:
            # Straight Flush
            if len(set(suits)) == 1:
                return 9, [values[-1]], 'Straight Flush'
            # Straight
            else:
                return 5, [values[-1]], 'Straight'

        elif len(set(values)) == 2:
            mode = moder(values)
            # Four of a Kind
            if values.count(mode) == 4:
                return 8, [mode], 'Four of a Kind'
            # Full House
            else:
                return 7, [mode], 'Full House'

        elif len(set(values)) == 3:
            mode = moder(values)
            # Three of a Kind
            if values.count(mode) == 3:
                return 4, [mode], 'Three of a Kind'
            # Two Pairs
            else:
                values.remove(mode)
                new_mode = moder(values)
                pairs = [mode, new_mode]
                return 3, sorted(pairs, reverse=True) + [x for x in values if x not in pairs], 'Two Pair'

        # One Pair
        elif len(set(values)) == 4:
            mode = moder(values)
            values.remove(mode)
            values.remove(mode)
            return 2, [mode] + sorted(values, reverse=True), 'One Pair'

        # Flush
        elif len(set(suits)) == 1:
            return 6, [values[::-1]], 'Flush'

        # High Card
        else:
            return 1, [values[::-1]], 'High Card'

    def score_hands(self):
        for player in [player for player in self.player_list if player.is_in]:

            best_hand_score, best_high_card, best_hand_string, best_hand = 0, [], None, []

            for trio in combinations(self.board, 3):
                combo = player.hole_cards + list(trio)
                hand = [(card.rank, card.suit) for card in combo]
                hand_score, high_card, hand_string = self.evaluate_hand(hand)

                if hand_score > best_hand_score:
                    best_hand_score = hand_score
                    best_high_card = high_card
                    best_hand_string = hand_string
                    best_hand = combo

                elif hand_score == best_hand_score:
                    high = True
                    i = 0
                    while high:
                        high = best_high_card[i] == high_card[i]
                        if not high and high_card[i] > best_high_card[i]:
                            best_high_card = high_card
                            best_hand = combo
                        if i + 1 == len(high_card):
                            high = False
                        i += 1

            player.hand_score = best_hand_score
            player.hand_string = best_hand_string
            player.best_hand = best_hand
            player.high_card = best_high_card

    def pick_winner(self):
        players = [player for player in self.player_list if player.is_in]
        print()
        if self.__len__() == 1:
            self.winner = players[0]

        else:

            player_scores = [player.hand_score for player in players]
            winner_score = max(player_scores)
            winners_index = [i for i, x in enumerate(player_scores) if x == winner_score]

            if len(winners_index) == 1:
                winner = players[winners_index[0]]
                self.winner = winner
                print(winner.name + ' wins with ' + winner.hand_string)

            else:
                potentials = [players[i] for i in winners_index]
                high_cards = [player.high_card for player in potentials]
                def sort_lists_maxes(*values):
                    return sorted(values, key=lambda x: sorted(x, reverse=True), reverse=True)[0]
                winner = potentials[[i for i, x in enumerate(high_cards) if x == sort_lists_maxes(*high_cards)][0]]
                self.winner = winner
                print(winner.name + ' wins with ' + winner.hand_string)

    def payout(self):
        self.winner.stack += self.total_pot
        print(self.winner.name + ' wins $' + str(self.total_pot - self.winner.pot_bet))

    def reset_players(self):
        for player in self.player_list:
            if player.stack <= 0:
                self.player_list.remove(player)
            else:
                player.reset()

    def play(self):
        i = 0
        while self.__len__() > 1 and i < 8:
            if i == 0:
                print('\nPlace Your Bets!')
                self.deal_cards()
            if i == 1:
                self.actions()
            if i == 2:
                print('\nThe Flop!')
                self.flop()
            if i == 3:
                self.actions()
            if i == 4:
                print('\nThe Turn!')
                self.turn()
            if i == 5:
                self.actions()
            if i == 6:
                print('\nThe River!')
                self.river()
            if i == 7:
                self.actions()

            if i % 2 == 0:
                for player in self.player_list:
                    if player.is_in:
                        print(player.name + ': ' + str([c.card for c in player.hole_cards]))

                if self.board:
                    print('Board: ' + str([c.card for c in self.board]))

                print('Pot Size: $' + str(self.total_pot))

            i += 1

        if self.__len__() > 1:
            self.score_hands()
        self.pick_winner()
        self.payout()
        self.reset_players()

        print('\nPlayers')
        for player in self.player_list:
            print('{}: ${}'.format(player.name, player.stack))
        print()
        return self.player_list



if __name__ == '__main__':

    play_again = True
    player_list = []
    name_list = []
    stack_list = []
    buyin_min = 10

    while play_again:

        if player_list:
            name_list = [player.name for player in player_list]
            stack_list = [player.stack for player in player_list]

            print('\nLeaderboard')
            leader_list = sorted(zip(name_list, stack_list), key=lambda x: x[1], reverse=True)
            for player in leader_list:
                print('{}: ${}'.format(player[0], player[1]))

        while True:
            # Update name_list to ensure there are no duplicates
            if player_list:
                print()
                name_list = [player.name for player in player_list]

            action = str(input('Add Player or Start? [Add/Start] ')).strip().lower()

            if action not in ['add', 'start']:
                print('Not a valid action! Must be \'add\' or \'start\'')
                continue

            else:
                # Start Action
                if action == 'start':
                    if len(player_list) < 2:
                        print('Not enough players to start! Add more players')
                        continue
                    else:
                        # Play the hand
                        hand = Hand(*player_list)
                        player_list = hand.play()
                        # Check to play again
                        again = str(input('Play Again? [y/n] ')).strip().lower()
                        if again in ['yes', 'y']:
                            play_again = True
                        else:
                            play_again =  False
                        break
                # Add Action
                else:
                    if len(player_list) == 10:
                        print('Table full! Start the game!')
                        continue
                    else:
                        name = str(input('Player Name (or \'Cancel\'): '))
                        # Check if name already in use
                        if name in name_list:
                            print('Name already exists! Name must be unique!')
                            continue
                        elif name.lower() == 'cancel':
                            continue
                        else:
                            try:
                                stack = int(input('Buy in amount (stack): $'))
                            except ValueError:
                                print('Must be a valid integer')
                                continue
                            if stack < buyin_min:
                                print('Must buy-in for more!')
                                continue
                            else:
                                player_list.append(Player(name, stack))
