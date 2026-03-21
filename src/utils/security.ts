/**
 * Security utilities for LaunchLens
 * - Data encryption/decryption
 * - Input sanitization
 * - CSRF protection
 */

/**
 * Sanitize user input to prevent XSS attacks
 */
export function sanitizeInput(input: string): string {
  if (!input) return '';

  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
}

/**
 * Encrypt sensitive data before storing in localStorage
 */
export function encryptData(data: unknown, key: string = 'launchlens-key'): string {
  try {
    const plaintext = JSON.stringify(data);
    const encoded = btoa(plaintext); // Base64 encoding as simple encryption
    const hash = generateSimpleHash(key);

    // XOR cipher with hash for additional security
    const encrypted = encoded.split('').map((char, i) => {
      return String.fromCharCode(char.charCodeAt(0) ^ hash.charCodeAt(i % hash.length));
    }).join('');

    return btoa(encrypted);
  } catch (error) {
    console.error('Encryption failed:', error);
    return '';
  }
}

/**
 * Decrypt data retrieved from localStorage
 */
export function decryptData<T = unknown>(encryptedData: string, key: string = 'launchlens-key'): T | null {
  try {
    const encrypted = atob(encryptedData);
    const hash = generateSimpleHash(key);

    // Reverse XOR cipher
    const decoded = encrypted.split('').map((char, i) => {
      return String.fromCharCode(char.charCodeAt(0) ^ hash.charCodeAt(i % hash.length));
    }).join('');

    const plaintext = atob(decoded);
    return JSON.parse(plaintext) as T;
  } catch (error) {
    console.error('Decryption failed:', error);
    return null;
  }
}

/**
 * Generate a simple hash from a string (for XOR encryption)
 */
function generateSimpleHash(input: string): string {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
}

/**
 * Generate CSRF token for form submissions
 */
export function generateCSRFToken(): string {
  const bytes = new Uint8Array(32);
  if (typeof window !== 'undefined' && window.crypto) {
    window.crypto.getRandomValues(bytes);
  } else {
    // Fallback for older browsers
    for (let i = 0; i < bytes.length; i++) {
      bytes[i] = Math.floor(Math.random() * 256);
    }
  }
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Validate CSRF token from session storage
 */
export function validateCSRFToken(token: string): boolean {
  const storedToken = sessionStorage.getItem('csrf-token');
  return storedToken === token;
}

/**
 * Store CSRF token in session storage
 */
export function storeCSRFToken(token: string): void {
  sessionStorage.setItem('csrf-token', token);
}

/**
 * Create secure headers for API requests
 */
export function getSecureHeaders(): Record<string, string> {
  const csrfToken = sessionStorage.getItem('csrf-token') || '';

  return {
    'X-CSRF-Token': csrfToken,
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  };
}

/**
 * Safely store sensitive data with encryption
 */
export function setSecureLocalStorage(key: string, data: unknown): void {
  try {
    const encrypted = encryptData(data);
    localStorage.setItem(`secure_${key}`, encrypted);
  } catch (error) {
    console.error('Failed to store secure data:', error);
  }
}

/**
 * Safely retrieve encrypted data from localStorage
 */
export function getSecureLocalStorage<T = unknown>(key: string): T | null {
  try {
    const encrypted = localStorage.getItem(`secure_${key}`);
    if (!encrypted) return null;
    return decryptData<T>(encrypted);
  } catch (error) {
    console.error('Failed to retrieve secure data:', error);
    return null;
  }
}

/**
 * Clear all secure data from localStorage
 */
export function clearSecureLocalStorage(): void {
  const keys = Object.keys(localStorage).filter(k => k.startsWith('secure_'));
  keys.forEach(key => localStorage.removeItem(key));
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Hash password using simple SHA-like approach (client-side)
 * NOTE: For production, use proper hashing on backend
 */
export function hashPassword(password: string): string {
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
  }
  return Math.abs(hash).toString(36);
}
