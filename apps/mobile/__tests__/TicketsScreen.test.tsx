import React from 'react';
import { render } from '@testing-library/react-native';
import TicketsScreen from '../app/tickets';

describe('TicketsScreen', () => {
  it('renders ticket creation modal trigger', () => {
    const { getByText } = render(<TicketsScreen />);
    expect(getByText(/Add Ticket/i)).toBeTruthy();
  });
});
