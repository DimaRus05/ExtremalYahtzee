import React from 'react';
import { DiceList } from './DiceList';
import { Stage1Table } from './Stage1Table';
import { useGameStore } from './gameStore';
import { Stage1Category } from './types';

const categories: Stage1Category[] = ['ones','twos','threes','fours','fives','sixes'];

export default function App() {
  const { hand, rollsLeft, rollDice, toggleHold, scoreStage1 } = useGameStore();

  return (
    <div style={{ textAlign: 'center', marginTop: 50 }}>
      <h1>Yahtzee Stage 1 Demo</h1>
      <DiceList hand={hand} onToggle={toggleHold} />
      <div style={{ margin: 20 }}>
        <button onClick={rollDice} disabled={rollsLeft === 0}>
          Бросить ({rollsLeft} осталось)
        </button>
      </div>
      <Stage1Table categories={categories} scoreFn={scoreStage1} />
    </div>
  );
}