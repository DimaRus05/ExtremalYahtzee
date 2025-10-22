import React from 'react';
import { Die } from './types';

type Props = { die: Die; onClick: () => void };

export const Dice: React.FC<Props> = ({ die, onClick }) => {
  return (
    <div
      onClick={onClick}
      style={{
        display: 'inline-block',
        width: 50,
        height: 50,
        lineHeight: '50px',
        textAlign: 'center',
        margin: 5,
        border: '2px solid black',
        backgroundColor: die.held ? 'lightgreen' : 'white',
        cursor: 'pointer',
        userSelect: 'none',
      }}
    >
      {die.value}
    </div>
  );
};