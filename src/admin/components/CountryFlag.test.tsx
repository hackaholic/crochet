import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import CountryFlag, { isValidIsoCountryCode, getCountryFlagEmoji } from './CountryFlag';

describe('CountryFlag component & helpers', () => {
  afterEach(() => {
    cleanup();
  });

  it('validates 2-letter ISO country codes correctly', () => {
    expect(isValidIsoCountryCode('IN')).toBe(true);
    expect(isValidIsoCountryCode('US')).toBe(true);
    expect(isValidIsoCountryCode('gb')).toBe(true);
    expect(isValidIsoCountryCode('UNKNOWN')).toBe(false);
    expect(isValidIsoCountryCode('')).toBe(false);
    expect(isValidIsoCountryCode(null)).toBe(false);
    expect(isValidIsoCountryCode(undefined)).toBe(false);
    expect(isValidIsoCountryCode('IND')).toBe(false);
    expect(isValidIsoCountryCode('12')).toBe(false);
  });

  it('generates regional indicator emoji for valid ISO codes', () => {
    const flag = getCountryFlagEmoji('IN');
    // Unicode Regional Indicator Symbol Letter I (U+1F1EE) and N (U+1F1F3)
    expect(flag).toBe('🇮🇳');
  });

  it('renders flag emoji element for valid country code', () => {
    render(<CountryFlag countryCode="IN" title="India" />);
    const flagEl = screen.getByTestId('country-flag-emoji');
    expect(flagEl).toBeInTheDocument();
    expect(flagEl).toHaveAttribute('aria-label', 'India');
    expect(flagEl.textContent).toBe('🇮🇳');
  });

  it('renders neutral globe SVG fallback for UNKNOWN or invalid codes', () => {
    render(<CountryFlag countryCode="UNKNOWN" />);
    const fallback = screen.getByTestId('country-flag-fallback');
    expect(fallback).toBeInTheDocument();
    expect(fallback).toHaveAttribute('aria-label', 'Unknown destination');
    expect(fallback.querySelector('svg')).toBeInTheDocument();
  });

  it('renders neutral globe SVG fallback for null / empty code', () => {
    render(<CountryFlag countryCode={null} />);
    const fallback = screen.getByTestId('country-flag-fallback');
    expect(fallback).toBeInTheDocument();
    expect(fallback.querySelector('svg')).toBeInTheDocument();
  });
});
