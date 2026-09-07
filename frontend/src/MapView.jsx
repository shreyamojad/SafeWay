import { useState,useEffect } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

const defaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,

  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function MapView({
  startCoordinates,
  destinationCoordinates,
  setRouteDistance,
  setRouteDuration
}) {
    const [routeCoordinates, setRouteCoordinates] = useState([]);
    const [routes, setRoutes] = useState([]);

    const [distance, setDistance] = useState(null);
const [duration, setDuration] = useState(null);

    const getRoute = async () => {
  if (!startCoordinates || !destinationCoordinates) {
    return;
  }

  const url =
    `https://router.project-osrm.org/route/v1/driving/` +
    `${startCoordinates[1]},${startCoordinates[0]};` +
    `${destinationCoordinates[1]},${destinationCoordinates[0]}` +
    `?overview=full&geometries=geojson&alternatives=true`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data.routes && data.routes.length > 0) {
      setRoutes(data.routes);

        const distanceInKm = data.routes[0].distance / 1000;
const durationInMinutes = data.routes[0].duration / 60;

setDistance(distanceInKm);
setDuration(durationInMinutes);

setRouteDistance(distanceInKm);
setRouteDuration(durationInMinutes);

      const coordinates = data.routes[0].geometry.coordinates.map(
        (coordinate) => [coordinate[1], coordinate[0]]
      );

      setRouteCoordinates(coordinates);
    }
  } catch (error) {
    console.error("Route calculation failed:", error);
  }
};

useEffect(() => {
  getRoute();
}, [startCoordinates, destinationCoordinates]);

  return (
    <MapContainer
      center={startCoordinates || [19.0760, 72.8777]}
      zoom={12}
      style={{ height: "500px", width: "100%" }}
    >

      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {startCoordinates && (
  <Marker
    position={startCoordinates}
    icon={defaultIcon}
  >
    <Popup>
      📍 Start Location
    </Popup>
  </Marker>
)}

      {destinationCoordinates && (
  <Marker
    position={destinationCoordinates}
    icon={defaultIcon}
  >
    <Popup>
      🏁 Destination
    </Popup>
  </Marker>
)}

{routeCoordinates.length > 0 && (
  <Polyline
    positions={routeCoordinates}
  />
)}
{routes.slice(1).map((route, index) => {
  const coordinates = route.geometry.coordinates.map(
    (coordinate) => [coordinate[1], coordinate[0]]
  );

  return (
    <Polyline
      key={index}
      positions={coordinates}
    />
  );
})}

    </MapContainer>
  );
}

export default MapView;