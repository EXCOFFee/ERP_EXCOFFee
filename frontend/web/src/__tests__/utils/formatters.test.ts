import { describe, it, expect } from 'vitest';
import { formatCurrency, formatDate, formatNumber, truncate, getInitials } from '../../utils/formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('should format currency with default locale', () => {
      const result = formatCurrency(1234.56);
      expect(result).toContain('1,234.56');
    });

    it('should format zero', () => {
      const result = formatCurrency(0);
      expect(result).toContain('0.00');
    });

    it('should format negative numbers', () => {
      const result = formatCurrency(-500.50);
      expect(result).toContain('500.50');
    });

    it('should handle different currencies', () => {
      const result = formatCurrency(1000, 'EUR');
      expect(result).toBeDefined();
    });
  });

  describe('formatDate', () => {
    it('should format date string', () => {
      const result = formatDate('2024-01-15');
      expect(result).toBeDefined();
    });

    it('should format Date object', () => {
      const date = new Date(2024, 0, 15);
      const result = formatDate(date);
      expect(result).toBeDefined();
    });
  });

  describe('formatNumber', () => {
    it('should format number with default decimals', () => {
      const result = formatNumber(1234);
      expect(result).toBe('1,234');
    });

    it('should format number with specified decimals', () => {
      const result = formatNumber(1234.5678, 2);
      expect(result).toBe('1,234.57');
    });
  });

  describe('truncate', () => {
    it('should truncate long strings', () => {
      const result = truncate('This is a very long string', 10);
      expect(result).toBe('This is a ...');
      expect(result.length).toBe(13);
    });

    it('should not truncate short strings', () => {
      const result = truncate('Short', 10);
      expect(result).toBe('Short');
    });

    it('should handle exact length', () => {
      const result = truncate('1234567890', 10);
      expect(result).toBe('1234567890');
    });
  });

  describe('getInitials', () => {
    it('should get initials from full name', () => {
      const result = getInitials('John Doe');
      expect(result).toBe('JD');
    });

    it('should handle single name', () => {
      const result = getInitials('John');
      expect(result).toBe('J');
    });

    it('should handle multiple names', () => {
      const result = getInitials('John Michael Doe');
      expect(result).toBe('JM');
    });

    it('should limit to max length', () => {
      const result = getInitials('John Michael Doe Smith', 3);
      expect(result).toBe('JMD');
    });
  });
});
