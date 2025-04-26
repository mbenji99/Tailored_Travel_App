// src/api.ts
const API = import.meta.env.VITE_API_URL || "";

// ── Auth ───────────────────────────────────────────────────────────────────────
export interface Credentials { email: string; password: string; }
export interface User { id: string; email: string; }

export async function login(creds: Credentials): Promise<User> {
  const res = await fetch(`${API}/api/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(creds),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || res.statusText);
  }
  return (await res.json()).user;
}

export async function register(creds: Credentials): Promise<void> {
  const res = await fetch(`${API}/api/register`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(creds),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || res.statusText);
  }
}

export async function logout(): Promise<void> {
  const res = await fetch(`${API}/api/logout`, { method: 'POST', credentials: 'include' });
  if (!res.ok) throw new Error('Logout failed');
}

export async function getSession(): Promise<User|null> {
  const res = await fetch(`${API}/api/session`, { credentials: 'include' });
  if (!res.ok) return null;
  return (await res.json()).user;
}

// ── Trips ──────────────────────────────────────────────────────────────────────
export interface Trip {
  id: number;
  user_id: string;
  destination: string;
  budget: number;
  remaining_budget: number;
  weather_preference: string;
  environment_preference: string;
  activity_preference: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export async function fetchTrips(): Promise<Trip[]> {
  const res = await fetch(`${API}/api/trips`, { credentials: 'include' });
  if (!res.ok) throw new Error('Unauthorized');
  return (await res.json()).trips;
}

export async function createTrip(payload: {
  destination: string;
  budget: number;
  weather_preference: string;
  environment_preference: string;
  activity_preference: string;
}): Promise<Trip> {
  const res = await fetch(`${API}/api/trips`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()).trip;
}

export async function fetchTrip(tripId: number): Promise<Trip> {
  const res = await fetch(`${API}/api/trips/${tripId}`, { credentials: 'include' });
  if (!res.ok) throw new Error('Trip not found');
  return (await res.json()).trip;
}

// ── Recommendations ────────────────────────────────────────────────────────────
export interface Recommendation {
  destination_id: string;
  predicted_rating: number;
  external_features: Record<string, number>;
}

export async function fetchRecommendation(
  destinationId: string
): Promise<Recommendation> {
  const endpoint = `${API}/api/recommend?destination_id=${encodeURIComponent(destinationId)}`;
  console.log(`🔗 GET ${endpoint}`);

  let res: Response;
  try {
    res = await fetch(endpoint, { credentials: 'include' });
  } catch (networkErr) {
    console.error(`🌐 Network error for ${destinationId}:`, networkErr);
    throw new Error('Network error: Cannot reach recommendation service');
  }

  let json: any;
  try {
    json = await res.json();
  } catch (parseErr) {
    console.error(`⚠️ JSON parse error for ${endpoint}:`, parseErr);
    throw new Error('Invalid response from recommendation service');
  }

  if (!res.ok) {
    console.error(`❌ Service error for ${destinationId}:`, json);
    throw new Error(json?.message || `Service responded ${res.status}`);
  }

  return json as Recommendation;
}

export async function fetchRecommendations(
  tripId: number,
  n = 3
): Promise<Recommendation[]> {
  const endpoint = `${API}/api/trips/${tripId}/recommendations?n=${n}`;
  console.log(`🔗 GET ${endpoint}`);
  const res = await fetch(endpoint, { credentials: 'include' });
  const json = await res.json().catch(() => null);
  console.log(`📥 Response for trip ${tripId}:`, json);
  if (!res.ok) throw new Error(json?.message || 'Recommendation error');
  return json.recommendations;
}

// ── Profile ────────────────────────────────────────────────────────────────────
export interface Profile { email: string; username: string; }

export async function fetchProfile(): Promise<Profile> {
  const res = await fetch(`${API}/api/profile`, { credentials: 'include' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Failed to load profile');
  }
  return await res.json();
}

export async function updateProfile(username: string): Promise<Profile> {
  const res = await fetch(`${API}/api/profile`, {
    method: 'PUT',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Failed to update profile');
  }
  return await res.json();
}
