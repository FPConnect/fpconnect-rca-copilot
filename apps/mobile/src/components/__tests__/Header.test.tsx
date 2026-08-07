import React from 'react';
import { render } from '@testing-library/react-native';
import Header from '../Header';

describe('Header', () => {
  it('renders title and notification badge', () => {
    const { getByText, getByA11yLabel } = render(
      <Header title="Test Title" notificationCount={3} />
    );
    expect(getByText('Test Title')).toBeTruthy();
    expect(getByText('FPConnect')).toBeTruthy();
    expect(getByText('Technologies')).toBeTruthy();
    expect(getByText('3')).toBeTruthy();
  });

  it('shows 9+ for notificationCount > 9', () => {
    const { getByText } = render(
      <Header title="Test Title" notificationCount={15} />
    );
    expect(getByText('9+')).toBeTruthy();
  });
});
