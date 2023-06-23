import { useMemo } from "react";
import { useMantineTheme } from "@mantine/core";
import { getCountryFromCoordinates } from "../utils/api";
import { getHeatColor, darkenColor, rgbToHex } from "../utils/colors";
import geoData from "../utils/geoData";

import "leaflet/dist/leaflet.css";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";

import Legend from "./Legend";

function Map({ getValue, gradient, onCountrySelect, minValue, maxValue }) {
  const getColor = getHeatColor(gradient, minValue, maxValue);

  const style = (feature) => {
    const countryId = feature.properties["ISO_A2"];
    const avgTemp = getValue(countryId);

    const heatColor = avgTemp ? getColor(avgTemp) : null;
    // const strokeColor = avgTemp ? rgbToHex(darkenColor(heatColor, 0.2)) : null;
    // TODO why is stroke color not working ?

    return {
      color: heatColor ? "white" : null,
      fillColor: heatColor || "transparent",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.7,
    };
  };

  const handleCountryClick = async (event) => {
    const lat = event.latlng.lat;
    const lng = event.latlng.lng;
    const countryInfo = await getCountryFromCoordinates(lat, lng);

    if (countryInfo) {
      onCountrySelect({
        id: countryInfo.countryCode.toUpperCase(),
        name: countryInfo.countryName,
      });
    }
  };

  const { colorScheme } = useMantineTheme();
  const tileLayerProps =
    colorScheme === "light"
      ? {
          url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        }
      : {
          url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        };

  return (
    <>
      <MapContainer
        zoomControl={false}
        center={[51.505, -0.09]}
        zoom={2.5}
        style={{
          height: "100%",
          width: "100%",
          position: "relative",
          zIndex: 1,
        }}
        worldCopyJump={true}
        maxBounds={[
          [-90, -180],
          [90, 180],
        ]}
        maxBoundsViscosity={1.0}
        minZoom={2}
        maxZoom={10}
      >
        <TileLayer {...tileLayerProps} />
        {geoData && (
          <GeoJSON
            style={style}
            data={geoData}
            eventHandlers={{ click: handleCountryClick }}
          />
        )}
      </MapContainer>
      <Legend min={minValue} max={maxValue} gradient={gradient} />
    </>
  );
}

export default Map;
