"""Основная логика игры в покер на костях"""

import random
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import uuid


class Combination(Enum):
    FIVE_OF_A_KIND = "Пять одинаковых"
    FOUR_OF_A_KIND = "Четыре одинаковых"
    FULL_HOUSE = "Фулл-хаус"
    STRAIGHT = "Стрит"
    THREE_OF_A_KIND = "Три одинаковых"
    TWO_PAIRS = "Две пары"
    ONE_PAIR = "Одна пара"
    HIGH_DIE = "Старшая кость"


class GameStatus(Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class Player:
    id: str
    name: str
    score: int = 0
    is_ready: bool = False


@dataclass
class Turn:
    player_id: str
    roll: List[int]
    combination: Combination
    score: int
    round_number: int
    timestamp: datetime


class DicePokerGame:
    def __init__(self, game_id: str, max_players: int = 4, max_rounds: int = 3):
        self.game_id = game_id
        self.max_players = max_players
        self.max_rounds = max_rounds
        self.players: Dict[str, Player] = {}
        self.status = GameStatus.WAITING
        self.current_round = 1
        self.current_player_index = 0
        self.current_roll = []
        self.remaining_rerolls = 2
        self.turns_history: List[Turn] = []
        self.created_at = datetime.now()

    def add_player(self, player_name: str) -> str:
        """Добавляет игрока в игру и возвращает его ID"""
        if len(self.players) >= self.max_players:
            raise ValueError("Достигнуто максимальное количество игроков")

        if any(p.name == player_name for p in self.players.values()):
            raise ValueError("Игрок с таким именем уже существует")

        player_id = str(uuid.uuid4())
        self.players[player_id] = Player(id=player_id, name=player_name)
        return player_id

    def start_game(self) -> bool:
        """Начинает игру, если готовы все игроки"""
        if len(self.players) < 2:
            return False

        if not all(player.is_ready for player in self.players.values()):
            return False

        self.status = GameStatus.ACTIVE
        self._start_new_turn()
        return True

    def _start_new_turn(self):
        """Начинает ход текущего игрока"""
        self.current_roll = self._roll_dice(5)
        self.remaining_rerolls = 2

    def _roll_dice(self, count: int) -> List[int]:
        return [random.randint(1, 6) for _ in range(count)]

    def get_current_player(self) -> Optional[Player]:
        """Возвращает текущего игрока"""
        if not self.players:
            return None
        player_ids = list(self.players.keys())
        return self.players[player_ids[self.current_player_index]]

    def reroll_dice(self, player_id: str, dice_to_reroll: List[int]) -> bool:
        """Перебрасывает выбранные кости"""
        if self.status != GameStatus.ACTIVE:
            return False

        current_player = self.get_current_player()
        if not current_player or current_player.id != player_id:
            return False

        if self.remaining_rerolls <= 0:
            return False

        # Перебрасываем выбранные кости
        for idx in dice_to_reroll:
            if 0 <= idx < 5:
                self.current_roll[idx] = random.randint(1, 6)

        self.remaining_rerolls -= 1
        return True

    def end_turn(self, player_id: str) -> bool:
        """Завершает ход текущего игрока"""
        if self.status != GameStatus.ACTIVE:
            return False

        current_player = self.get_current_player()
        if not current_player or current_player.id != player_id:
            return False

        # Вычисляем комбинацию и очки
        combination = self._evaluate_combination(self.current_roll)
        score = self._calculate_score(combination, self.current_roll)

        # Обновляем счет игрока
        current_player.score += score

        # Сохраняем ход в историю
        turn = Turn(
            player_id=current_player.id,
            roll=self.current_roll.copy(),
            combination=combination,
            score=score,
            round_number=self.current_round,
            timestamp=datetime.now(),
        )
        self.turns_history.append(turn)

        # Переходим к следующему игроку или раунду
        return self._next_turn()

    def _next_turn(self) -> bool:
        """Переходит к следующему ходу"""
        self.current_player_index += 1

        # Если все игроки сходили в этом раунде
        if self.current_player_index >= len(self.players):
            self.current_player_index = 0
            self.current_round += 1

            # Проверяем окончание игры
            if self.current_round > self.max_rounds:
                self.status = GameStatus.COMPLETED
                return True

        self._start_new_turn()
        return True

    def _evaluate_combination(self, dice: List[int]) -> Combination:
        dice_counts = self._count_dice(dice)
        values = list(dice_counts.values())
        dice_values = list(dice_counts.keys())

        if 5 in values:
            return Combination.FIVE_OF_A_KIND
        elif 4 in values:
            return Combination.FOUR_OF_A_KIND
        elif 3 in values and 2 in values:
            return Combination.FULL_HOUSE
        elif 3 in values:
            return Combination.THREE_OF_A_KIND
        elif values.count(2) == 2:
            return Combination.TWO_PAIRS
        elif 2 in values:
            return Combination.ONE_PAIR
        elif self._is_straight(dice_values):
            return Combination.STRAIGHT
        else:
            return Combination.HIGH_DIE

    def _count_dice(self, dice: List[int]) -> Dict[int, int]:
        counts = {}
        for die in dice:
            counts[die] = counts.get(die, 0) + 1
        return counts

    def _is_straight(self, dice_values: List[int]) -> bool:
        unique_values = sorted(set(dice_values))
        if len(unique_values) != 5:
            return False
        return unique_values == [1, 2, 3, 4, 5] or unique_values == [2, 3, 4, 5, 6]

    def _calculate_score(self, combination: Combination, dice: List[int]) -> int:
        score_table = {
            Combination.FIVE_OF_A_KIND: 100,
            Combination.FOUR_OF_A_KIND: 40,
            Combination.FULL_HOUSE: 25,
            Combination.STRAIGHT: 20,
            Combination.THREE_OF_A_KIND: 15,
            Combination.TWO_PAIRS: 10,
            Combination.ONE_PAIR: 5,
            Combination.HIGH_DIE: max(dice),
        }
        return score_table.get(combination, 0)

    def get_game_state(self, for_player_id: str | None = None) -> Dict:
        """Возвращает состояние игры для клиента"""
        current_player = self.get_current_player()

        # Сортируем игроков по очкам
        sorted_players = sorted(
            self.players.values(), key=lambda p: p.score, reverse=True
        )

        # Определяем current_turn в зависимости от статуса
        current_turn = None
        if self.status == GameStatus.ACTIVE:
            combination = None
            if self.current_roll:
                combination = self._evaluate_combination(self.current_roll).value

            current_turn = {
                "roll": self.current_roll,
                "remaining_rerolls": self.remaining_rerolls,
                "combination": combination,
            }

        # Определяем winner в зависимости от статуса
        winner = None
        if self.status == GameStatus.COMPLETED:
            winner = self._get_winner()

        state = {
            "game_id": self.game_id,
            "status": self.status.value,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "score": p.score,
                    "is_ready": p.is_ready,
                    "is_current": (
                        p.id == current_player.id if current_player else False
                    ),
                }
                for p in sorted_players
            ],
            "current_turn": current_turn,
            "winner": winner,
        }

        return state

    def _get_winner(self) -> Dict | None:
        """Определяет победителя игры"""
        if not self.players:
            return None

        winner = max(self.players.values(), key=lambda p: p.score)
        return {"id": winner.id, "name": winner.name, "score": winner.score}

    def set_player_ready(self, player_id: str) -> bool:
        """Отмечает игрока как готового"""
        if player_id in self.players:
            self.players[player_id].is_ready = True
            return True
        return False


class GameManager:
    """Менеджер для управления всеми играми"""

    def __init__(self):
        self.games: Dict[str, DicePokerGame] = {}

    def create_game(self, max_players: int = 4, max_rounds: int = 3) -> str:
        """Создает новую игру и возвращает её ID"""
        game_id = str(uuid.uuid4())
        self.games[game_id] = DicePokerGame(game_id, max_players, max_rounds)
        return game_id

    def get_game(self, game_id: str) -> Optional[DicePokerGame]:
        """Возвращает игру по ID"""
        return self.games.get(game_id)

    def remove_game(self, game_id: str):
        """Удаляет игру"""
        if game_id in self.games:
            del self.games[game_id]
