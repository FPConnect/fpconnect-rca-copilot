import React from 'react';
import { render } from '@testing-library/react-native';
import DemoRecursos from '../app/demoRecursos';

describe('DemoRecursos', () => {
  it('renders ROI section', () => {
    const { getByText } = render(<DemoRecursos />);
    expect(getByText(/ROI/i)).toBeTruthy();
  });
});
