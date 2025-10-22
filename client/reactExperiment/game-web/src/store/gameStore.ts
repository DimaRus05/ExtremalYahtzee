// src/store/gameStore.ts
import { useState } from 'react';
import { DieValue, Die, Stage1Category } from '../types';

export function useGameStore() {
  const [hand, setHand] = useState<Die[]>([
    { value: 1, held: false },
    { value: 1, held: false },
    { value: 1, held: false },
    {  value: 1, held: false },
    { value: 1, held: false }
  ]);
  const [rollsLeft, setRollsLeft] = useState(3);
  const [stage1Scores, setStage1Scores] = useState<Partial<Record<Stage1Category, number>>>({});
  const scoreStage1 = (category: Stage1Category): number => {
    const f = { ones:1, twos:2, threes:3, fours:4, fives:5, sixes:6 }[category];
    const count = hand.filter(d => d.value === f).length;
    if (count === 3) return 0;
    return (count - 3) * f;
  };

  function rollDice() {
    if (rollsLeft === 0) return;
    setHand(prev =>
      prev.map(d => d.held ? d : { ...d, value: Math.floor(Math.random() * 6) + 1 as DieValue })
    );
    setRollsLeft(prev => prev - 1);
  }

  function toggleHold(index: number) {
    setHand(prev => prev.map((d, i) => i === index ? { ...d, held: !d.held } : d));
  }

  function commitStage1(cat: Stage1Category) {
    if (stage1Scores[cat] !== undefined) return;
    const values = hand.map(d => d.value);
    const score = scoreStage1(cat);
    setStage1Scores(prev => ({ ...prev, [cat]: score }));
    // Сброс руки для нового хода
    setHand(prev => prev.map(d => ({ ...d, held: false })));
    setRollsLeft(3);
  }

  return { hand, rollsLeft, stage1Scores, rollDice, toggleHold, commitStage1 };
}
