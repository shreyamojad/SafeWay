import { useState } from "react";
import MapView from "./MapView";
import Navbar from "./components/Navbar";
import SafetyScore from "./components/SafetyScore";
import RiskLevel from "./components/RiskLevel";
import SafetyFactors from "./components/SafetyFactors";
import Loading from "./components/Loading";
import RouteCard from "./components/RouteCard";

function App() {
  const [safetyScore, setSafetyScore] = useState(null);

  const [routePreference, setRoutePreference] = useState("safest");

  let riskLevel = "";

  if (safetyScore === null) {
    riskLevel = "--";
  } else if (safetyScore >= 80) {
    riskLevel = "Low";
  } else if (safetyScore >= 60) {
    riskLevel = "Medium";
  } else {
    riskLevel = "High";
  }

  const [isLoading, setIsLoading] = useState(false);

  const [startLocation, setStartLocation] = useState("");
  const [destination, setDestination] = useState("");

  const [startCoordinates, setStartCoordinates] = useState(null);
  const [destinationCoordinates, setDestinationCoordinates] = useState(null);

  const [routeDistance, setRouteDistance] = useState(null);
  const [routeDuration, setRouteDuration] = useState(null);

  const handleFindRoute = async () => {
    setIsLoading(true);

    setSafetyScore(null);

    console.log("1. Start Location:", startLocation);
    console.log("2. Destination:", destination);
    console.log("3. Route Preference:", routePreference);

    try {
      const startURL =
        `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(startLocation)}`;

      const destinationURL =
        `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(destination)}`;

      console.log("4. Searching for start location...");

      const startResponse = await fetch(startURL);

      console.log(
        "5. Start response received:",
        startResponse.status
      );

      const startData = await startResponse.json();

      if (startData.length === 0) {
        throw new Error("Starting location not found");
      }

      const startCoords = [
        parseFloat(startData[0].lat),
        parseFloat(startData[0].lon)
      ];

      setStartCoordinates(startCoords);

      console.log("6. Start Coordinates:", startCoords);

      console.log("7. Searching for destination...");

      const destinationResponse = await fetch(destinationURL);

      console.log(
        "8. Destination response received:",
        destinationResponse.status
      );

      const destinationData = await destinationResponse.json();

      if (destinationData.length === 0) {
        throw new Error("Destination not found");
      }

      const destinationCoords = [
        parseFloat(destinationData[0].lat),
        parseFloat(destinationData[0].lon)
      ];

      setDestinationCoordinates(destinationCoords);

      console.log("9. Destination Coordinates:", destinationCoords);

      console.log(
        "10. Selected route preference:",
        routePreference
      );

    } catch (error) {
      console.error("❌ Location search failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">

      <Navbar />

      <h1 className="app-title">
        SafeWay
      </h1>

      <p className="app-subtitle">
        Real-Time Route Safety Scoring & Risk Assessment Platform
      </p>

      <input
        type="text"
        className="location-input"
        placeholder="Enter starting location"
        value={startLocation}
        onChange={(event) => setStartLocation(event.target.value)}
      />

      <br />
      <br />

      <input
        type="text"
        className="location-input"
        placeholder="Enter destination"
        value={destination}
        onChange={(event) => setDestination(event.target.value)}
      />

      <div className="route-preference">

        <h2>Choose Route Preference</h2>

        <div className="preference-options">

          <label>
            <input
              type="radio"
              name="routePreference"
              value="fastest"
              checked={routePreference === "fastest"}
              onChange={(event) =>
                setRoutePreference(event.target.value)
              }
            />
            Fastest
          </label>

          <label>
            <input
              type="radio"
              name="routePreference"
              value="balanced"
              checked={routePreference === "balanced"}
              onChange={(event) =>
                setRoutePreference(event.target.value)
              }
            />
            Balanced
          </label>

          <label>
            <input
              type="radio"
              name="routePreference"
              value="safest"
              checked={routePreference === "safest"}
              onChange={(event) =>
                setRoutePreference(event.target.value)
              }
            />
            Safest
          </label>

        </div>

      </div>

      <br />

      <button
        className="route-button"
        onClick={handleFindRoute}
      >
        Find Safe Route
      </button>

      {isLoading && <Loading />}

      <br />
      <br />

      <MapView
        startCoordinates={startCoordinates}
        destinationCoordinates={destinationCoordinates}
        setRouteDistance={setRouteDistance}
        setRouteDuration={setRouteDuration}
      />

      {routeDistance !== null && (
        <div className="route-info">

          <h2>🛣️ Route Information</h2>

          <p>
            📏 Distance:{" "}
            <strong>
              {routeDistance.toFixed(2)} km
            </strong>
          </p>

          <p>
            ⏱️ Estimated Time:{" "}
            <strong>
              {Math.round(routeDuration)} minutes
            </strong>
          </p>

          <p>
            🎯 Preference:{" "}
            <strong>
              {routePreference.charAt(0).toUpperCase() +
                routePreference.slice(1)}
            </strong>
          </p>

        </div>
      )}

      {routeDistance !== null && (
        <>
          <SafetyScore score={safetyScore} />

          <RouteCard
            distance={routeDistance}
            duration={routeDuration}
            safetyScore={safetyScore}
          />

          <RiskLevel risk={riskLevel} />

          <SafetyFactors
            factors={
              safetyScore === null
                ? [
                    "Waiting for traffic analysis",
                    "Waiting for crime risk analysis",
                    "Waiting for road condition analysis"
                  ]
                : safetyScore >= 80
                ? [
                    "Low traffic congestion",
                    "Low crime risk",
                    "Good road conditions"
                  ]
                : safetyScore >= 60
                ? [
                    "Moderate traffic congestion",
                    "Moderate crime risk",
                    "Average road conditions"
                  ]
                : [
                    "High traffic congestion",
                    "Higher crime risk",
                    "Poor road conditions"
                  ]
            }
          />
        </>
      )}

    </div>
  );
}

export default App;