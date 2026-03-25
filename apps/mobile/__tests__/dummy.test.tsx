import React from 'react';
import { render } from '@testing-library/react-native';
import { Text } from 'react-native';

describe('Mobile Dummy Test', () => {
  it('renders a simple text', () => {
    const { getByText } = render(<Text>Mobile test funcionando!</Text>);
    expect(getByText('Mobile test funcionando!')).toBeTruthy();
  });
});
