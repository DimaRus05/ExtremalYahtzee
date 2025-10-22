import React from 'react';
import { Stage1Category } from './types';

type Props = {
  categories: Stage1Category[];
  scoreFn: (cat: Stage1Category) => number;
};

export const Stage1Table: React.FC<Props> = ({ categories, scoreFn }) => {
  return (
    <table style={{ borderCollapse: 'collapse', marginTop: 20 }}>
      <thead>
        <tr>
          {categories.map(c => (
            <th key={c} style={{ border: '1px solid black', padding: 5 }}>{c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        <tr>
          {categories.map(c => (
            <td key={c} style={{ border: '1px solid black', padding: 5, textAlign: 'center' }}>
              {scoreFn(c)}
            </td>
          ))}
        </tr>
      </tbody>
    </table>
  );
};