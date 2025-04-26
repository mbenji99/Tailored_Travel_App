// src/pages/TripDetails.tsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  fetchTrip,
  fetchRecommendations,
  Trip,
  Recommendation,
} from "../api";

export default function TripDetails() {
  const { tripId } = useParams<{ tripId: string }>();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (!tripId) {
      setError("No trip ID provided.");
      setLoading(false);
      return;
    }

    const id = parseInt(tripId, 10);
    if (isNaN(id)) {
      setError(`Invalid trip ID: ${tripId}`);
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const t = await fetchTrip(id);
        setTrip(t);

        const r = await fetchRecommendations(id, 3);
        setRecs(r);
      } catch (e) {
        setError("Trip not found or network error.");
      } finally {
        setLoading(false);
      }
    })();
  }, [tripId]);

  if (loading) return <div>Loading…</div>;
  if (error)  return <div className="text-red-600 font-semibold">{error}</div>;
  if (!trip) return <div>Trip not found</div>;

  // Coerce budget to number (handles both string and number inputs)
  const rawBudget = trip.budget as unknown;
  const budgetNum =
    typeof rawBudget === "number"
      ? rawBudget
      : parseFloat(String(rawBudget));
  const displayBudget = isNaN(budgetNum)
    ? "N/A"
    : `$${budgetNum.toFixed(2)}`;

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">
        Your Trip to {trip.destination}
      </h1>
      <p>Budget: {displayBudget}</p>
      <p>Status: {trip.status}</p>

      <section>
        <h2 className="text-2xl font-semibold mb-4">
          Top Recommendations
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {recs.map((r) => {
            // Ensure predicted_rating is numeric too
            const score =
              typeof r.predicted_rating === "number"
                ? r.predicted_rating
                : parseFloat(String(r.predicted_rating));
            const displayScore = isNaN(score)
              ? "—"
              : score.toFixed(1);

            return (
              <div
                key={r.destination_id}
                className="bg-white rounded-xl shadow-sm p-6 space-y-2"
              >
                <img
                  src={`https://source.unsplash.com/featured/?${r.destination_id}`}
                  alt={r.destination_id}
                  className="w-full h-36 object-cover rounded"
                />
                <h3 className="text-xl font-semibold">
                  {r.destination_id}
                </h3>
                <p>Predicted score: {displayScore}</p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
