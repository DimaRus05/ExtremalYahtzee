import { useState } from 'react';
import { Die, Stage1Category } from './types';

export function useGameStore() {
  const [hand, setHand] = useState<Die[]>([
    { value: 1, held: false },
    { value: 1, held: false },
    { value: 1, held: false },
    { value: 1, held: false },
    { value: 1, held: false },
  ]);
  const [rollsLeft, setRollsLeft] = useState(3);

  const rollDice = () => {
    if (rollsLeft === 0) return;
    setHand(h => h.map(d => (d.held ? d : { ...d, value: Math.floor(Math.random() * 6) + 1 })));
    setRollsLeft(r => r - 1);
  };

  const toggleHold = (index: number) => {
    setHand(h => h.map((d, i) => (i === index ? { ...d, held: !d.held } : d)));
  };

  const scoreStage1 = (category: Stage1Category) => {
    const f = { ones: 1, twos: 2, threes: 3, fours: 4, fives: 5, sixes: 6 }[category];
    const count = hand.filter(d => d.value === f).length;
    if (count === 3) return 0;
    return (count - 3) * f;
  };

  return { hand, rollsLeft, rollDice, toggleHold, scoreStage1 };
}