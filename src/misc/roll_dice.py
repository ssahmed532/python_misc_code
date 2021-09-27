import random
from typing import Tuple


class Dice:
    def __init__(self) -> None:
        self.faces: Tuple[int, int] = (0, 0)

    def roll(self) -> None:
        self.faces = (random.randint(1,6), random.randint(1, 6))

    def total(self) -> int:
        return sum(self.faces)

    def hardway(self) -> bool:
        return self.faces[0] == self.faces[1]

    def easyway(self) -> bool:
        return self.faces[0] != self.faces[1]

    def __str__(self) -> str:
        return f'Dice ({self.faces[0]}, {self.faces[1]})'


if __name__ == '__main__':
    d1 = Dice()
    d1.roll()
    print(d1)
