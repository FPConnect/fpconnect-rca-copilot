import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

test('dummy test - frontend setup', () => {
  render(<div>Vitest está funcionando!</div>);
  expect(screen.getByText('Vitest está funcionando!')).toBeInTheDocument();
});
