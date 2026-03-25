import React from 'react';
import { render } from '@testing-library/react-native';
import SettingsScreen from '../app/settings';

describe('SettingsScreen', () => {
  it('renders profile name input', () => {
    const { getByDisplayValue } = render(<SettingsScreen />);
    expect(getByDisplayValue('Admin')).toBeTruthy();
  });
});
