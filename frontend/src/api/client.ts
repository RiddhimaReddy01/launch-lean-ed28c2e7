/**
 * Core API client with authentication and error handling
 * Base request function used by all API modules
 */

import { queryClient } from '@/App';

// Primary and fallback API endpoints
const PRIMARY_URL = import.meta.env.VITE_API_URL || '';
const FALLBACK_URL = import.meta.env.VITE_API_FALLBACK_URL || '';
const PRIMARY_TIMEOUT = parseInt(import.meta.env.VITE_API_PRIMARY_TIMEOUT || '5000', 10);
const FALLBACK_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '90000', 10);

// Export both URLs for configuration purposes
export const API_BASE = PRIMARY_URL.trim().replace(/\/+$/, '');
export const API_FALLBACK = FALLBACK_URL.trim().replace(/\/+$/, '');
const API_TIMEOUT = FALLBACK_TIMEOUT;

export class APIError extends Error {
  constructor(
    public status: number,
    public detail: string,
    message: string = `API Error ${status}`,
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Attempt a request to a specific endpoint
 */
async function attemptRequest<T>(
  baseUrl: string,
  path: string,
  options: RequestInit = {},
  timeout: number,
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    const url = `${baseUrl}${normalizedPath}`;

    // Get auth token if available
    const token = localStorage.getItem('auth_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(url, {
      headers,
      signal: controller.signal,
      ...options,
    });

    if (!res.ok) {
      const detail = await res.text();
      if (res.status === 401) {
        localStorage.removeItem('auth_token');
        queryClient.clear();
        window.location.href = '/auth';
      }
      throw new APIError(res.status, detail, `API error ${res.status}`);
    }

    let data: T;
    try {
      data = await res.json() as T;
    } catch (parseError) {
      throw new APIError(500, 'Invalid response from server', 'Failed to parse response');
    }

    return data;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Core request function with fallback support
 * Tries primary endpoint first, falls back to fallback endpoint if primary fails/times out
 */
export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  if (!API_BASE) {
    throw new Error('Missing VITE_API_URL. Set it in project settings before making API requests.');
  }

  const primaryUrl = `${API_BASE}${normalizedPath}`;

  // Log API call in development
  if (import.meta.env.DEV) {
    console.log(`📤 API: ${options.method || 'GET'} ${primaryUrl}`);
  }

  // Try primary endpoint
  try {
    const data = await attemptRequest<T>(API_BASE, normalizedPath, options, PRIMARY_TIMEOUT);
    if (import.meta.env.DEV) {
      console.log(`✅ API: ${options.method || 'GET'} ${primaryUrl} (primary)`);
    }
    return data;
  } catch (primaryError) {
    if (import.meta.env.DEV) {
      console.warn(`⚠️  Primary endpoint failed: ${primaryError instanceof Error ? primaryError.message : 'Unknown error'}`);
    }

    // If no fallback configured, throw the primary error
    if (!API_FALLBACK) {
      if (primaryError instanceof APIError) {
        throw primaryError;
      }
      if (primaryError instanceof Error && primaryError.name === 'AbortError') {
        throw new Error(`Request timeout (${PRIMARY_TIMEOUT}ms)`);
      }
      throw primaryError;
    }

    // Try fallback endpoint
    const fallbackUrl = `${API_FALLBACK}${normalizedPath}`;
    if (import.meta.env.DEV) {
      console.log(`🔄 Attempting fallback: ${options.method || 'GET'} ${fallbackUrl}`);
    }

    try {
      const data = await attemptRequest<T>(API_FALLBACK, normalizedPath, options, FALLBACK_TIMEOUT);
      if (import.meta.env.DEV) {
        console.log(`✅ API: ${options.method || 'GET'} ${fallbackUrl} (fallback)`);
      }
      return data;
    } catch (fallbackError) {
      if (import.meta.env.DEV) {
        console.error(`❌ Both endpoints failed. Primary: ${primaryError instanceof Error ? primaryError.message : 'Unknown'}, Fallback: ${fallbackError instanceof Error ? fallbackError.message : 'Unknown'}`);
      }
      // Throw fallback error as it's the last attempt
      if (fallbackError instanceof APIError) {
        throw fallbackError;
      }
      if (fallbackError instanceof Error && fallbackError.name === 'AbortError') {
        throw new Error(`Request timeout (${FALLBACK_TIMEOUT}ms)`);
      }
      throw fallbackError;
    }
  }
}
