/**
 * Core API client with authentication and error handling
 * Base request function used by all API modules
 */

const rawUrl = import.meta.env.VITE_API_URL || '';
// Strip accidental "VITE_API_URL=" prefix from misconfigured secret
const API_BASE = rawUrl.replace(/^VITE_API_URL=/i, '').replace(/\/+$/, '') || 'https://launch-lean-backend.onrender.com';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10);

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
 * Core request function for all API calls
 * Handles authentication, timeouts, and error handling
 */
export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    // Get auth token if available
    const token = localStorage.getItem('auth_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const url = `${API_BASE}${path}`.replace(/\/$/, '');

    // Log API call in development
    if (import.meta.env.DEV) {
      console.log(`📤 API: ${options.method || 'GET'} ${url}`);
    }

    const res = await fetch(url, {
      headers,
      signal: controller.signal,
      ...options,
    });

    if (!res.ok) {
      const detail = await res.text();

      // Log error in development
      if (import.meta.env.DEV) {
        console.error(`❌ API Error ${res.status}: ${detail}`);
      }

      // Handle auth errors
      if (res.status === 401) {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }

      throw new APIError(res.status, detail, `API error ${res.status}`);
    }

    const data = await res.json() as T;

    // Log success in development
    if (import.meta.env.DEV) {
      console.log(`✅ API: ${options.method || 'GET'} ${url}`);
    }

    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout (${API_TIMEOUT}ms)`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
