import React from 'react';
import { render } from '@testing-library/react-native';
import DashboardScreen from '../app/index';

describe('DashboardScreen', () => {
  it('renders greeting and admin name', () => {
    const { getByText } = render(<DashboardScreen />);
    expect(getByText(/Good (morning|afternoon|evening)/)).toBeTruthy();
    expect(getByText('Admin')).toBeTruthy();
  });
});
