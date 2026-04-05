import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

test('dummy test - frontend setup', () => {
  render(React.createElement('div', null, 'Vitest está funcionando!'));
  expect(screen.getByText('Vitest está funcionando!')).toBeInTheDocument();
});
