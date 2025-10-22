import React from 'react';
import { Dice } from './Dice';
import { Die } from './types';

type Props = { hand: Die[]; onToggle: (index: number) => void };

export const DiceList: React.FC<Props> = ({ hand, onToggle }) => {
  return (
    <div>
      {hand.map((d, i) => (
        <Dice key={i} die={d} onClick={() => onToggle(i)} />
      ))}
    </div>
  );
};