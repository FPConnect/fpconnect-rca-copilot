import React from 'react';
import { render } from '@testing-library/react-native';
import MachinesScreen from '../app/machines';

describe('MachinesScreen', () => {
  it('renders search input', () => {
    const { getByPlaceholderText } = render(<MachinesScreen />);
    expect(getByPlaceholderText('Search machines...')).toBeTruthy();
  });
});
