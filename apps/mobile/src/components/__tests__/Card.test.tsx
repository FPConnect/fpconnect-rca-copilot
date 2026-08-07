import React from 'react';
import { render } from '@testing-library/react-native';
import Card from '../Card';

describe('Card', () => {
  it('renders label and value', () => {
    const { getByText } = render(
      <Card label="Test Label" value={42} backgroundColor="#fff" textColor="#000" />
    );
    expect(getByText('Test Label')).toBeTruthy();
    expect(getByText('42')).toBeTruthy();
  });

  it('renders icon if provided', () => {
    const icon = <>{'icon'}</>;
    const { getByText } = render(
      <Card label="Label" value={1} icon={icon} />
    );
    expect(getByText('icon')).toBeTruthy();
  });
});
