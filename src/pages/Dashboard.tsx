// src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate }              from 'react-router-dom';
import { useAuthStore }             from '../store/authStore';
import { fetchTrips }               from '../api';

interface Trip {
  id:               string;
  destination:      string;
  budget:           number | string;
  remaining_budget: number | string;
  status:           string;
  created_at:       string;
}

export default function Dashboard() {
  const [trips, setTrips]     = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const user                  = useAuthStore(s => s.user);
  const navigate              = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    fetchTrips()
      .then(fetched => setTrips(fetched))
      .catch(err => {
        console.error('Error fetching trips:', err);
        // you might redirect to login on 401 here
      })
      .finally(() => setLoading(false));
  }, [user, navigate]);

  if (loading) {
    return <div className="p-6">Loading your trips…</div>;
  }

  return (
    <div className="space-y-8 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">My Trips</h1>
        <button
          onClick={() => navigate('/new-trip')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Plan New Trip
        </button>
      </div>

      {trips.length === 0 ? (
        <div className="text-center py-12 bg-white rounded shadow">
          <p>You haven’t planned any trips yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map(trip => (
            <div
              key={trip.id}
              className="bg-white p-6 rounded shadow hover:shadow-lg transition"
            >
              <h2 className="text-xl font-semibold">{trip.destination}</h2>
              <p>Budget: ${Number(trip.budget).toFixed(2)}</p>
              <p>Remaining: ${Number(trip.remaining_budget).toFixed(2)}</p>
              <p>Status: {trip.status}</p>
              <button
                onClick={() => navigate(`/trips/${trip.id}`)}
                className="mt-4 px-4 py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-50"
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
