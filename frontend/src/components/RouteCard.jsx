function RouteCard({ distance, duration, safetyScore }) {
  return (
    <div className="route-card">
      <h2>🛣️ Recommended Route</h2>

      <p>
        📏 Distance:{" "}
        <strong>
          {distance !== null && distance !== undefined
            ? `${distance.toFixed(2)} km`
            : "--"}
        </strong>
      </p>

      <p>
        ⏱️ Estimated Time:{" "}
        <strong>
          {duration !== null && duration !== undefined
            ? `${Math.round(duration)} minutes`
            : "--"}
        </strong>
      </p>

      <p>
        🛡️ Safety Score:{" "}
        <strong>
          {safetyScore !== null && safetyScore !== undefined
            ? `${safetyScore}/100`
            : "--"}
        </strong>
      </p>

      <p>
        ⭐ Recommended safest route
      </p>
    </div>
  );
}

export default RouteCard;