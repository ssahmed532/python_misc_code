#
# Another basic and simple example of the Strategy design pattern demonstrated
# using the classic Rock, Paper, Scissors game.
#
# Code taken from:
#
#       https://auth0.com/blog/strategy-design-pattern-in-python/
#

import random
from abc import ABC, abstractmethod


ROCK = "Rock"
PAPER = "Paper"
SCISSORS = "Scissors"


# Strategy interface
class RPSStrategy(ABC):
    @abstractmethod
    def selection(self) -> str:
        pass


# Concrete strategies
class Rock(RPSStrategy):
    def selection(self) -> str:
        return ROCK

    def __str__(self) -> str:
        return ROCK + " selection strategy"


class Paper(RPSStrategy):
    def selection(self) -> str:
        return PAPER

    def __str__(self) -> str:
        return PAPER + " selection strategy"


class Scissors(RPSStrategy):
    def selection(self) -> str:
        return SCISSORS

    def __str__(self) -> str:
        return SCISSORS + " selection strategy"


class Random(RPSStrategy):
    def selection(self) -> str:
        options = [ROCK, PAPER, SCISSORS]
        return random.choice(options)

    def __str__(self) -> str:
        return "Random choice selection strategy"


# Context class
class Game:
    strategy: RPSStrategy

    def __init__(self, strategy: RPSStrategy = None) -> None:
        if strategy is not None:
            self.strategy = strategy
        else:
            self.strategy = Random()

        print(f"Game strategy is: {strategy}")

    def play(self, sec: RPSStrategy) -> None:
        s1 = self.strategy.selection()
        print(f"My selection is: {s1}")
        s2 = sec.strategy.selection()
        print(f"Other player has selected: {s2}")

        if s1 == s2:
            print("It's a tie")
        elif s1 == ROCK:
            if s2 == SCISSORS:
                print("Player 1 wins!")
            else:
                print("Player 2 wins!")
        elif s1 == SCISSORS:
            if s2 == PAPER:
                print("Player 1 wins!")
            else:
                print("Player 2 wins!")
        elif s1 == PAPER:
            if s2 == ROCK:
                print("Player 1 wins!")
            else:
                print("Player 2 wins!")


if __name__ == "__main__":
    player1 = Game(Random())
    player2 = Game(Rock())

    player1.play(player2)
