import random

class FstStage():
    def __init__(self, combination: int):
        self.dices_list: list[int] = []

        assert 1 <= combination <= 6
        self.combination: int = combination
    
    def throw_dice(self) -> int:
        dice = random.randint(1, 6)
        self.dices_list.append(dice)
        return dice
    
    def change_combination(self, new_combination: int):
        assert 1 <= new_combination <= 6
        self.combination = new_combination
    
    def get_score(self) -> int:
        return (self.dices_list.count(self.combination) - 3) * self.combination