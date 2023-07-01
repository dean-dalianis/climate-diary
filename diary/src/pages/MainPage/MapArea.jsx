import moment from "moment";

import { useMemo } from "react";
import { useMantineTheme } from "@mantine/core";

import Map from "../../components/Map";

function MapArea({ data, selectedDate, onCountrySelect }) {
  const theme = useMantineTheme();

  const mapData = useMemo(() => {
    let mapData = {};
    if (!data) return mapData;

    for (const { country_iso, time, value } of data) {
      if (!mapData[country_iso]) {
        mapData[country_iso] = {};
      }
      mapData[country_iso][moment(time).format("YYYY-MM-DD")] = value;
    }
    return mapData;
  }, [data]);

  const { min, max } = useMemo(() => {
    if (data.length === 0) {
      return { min: 0, max: 10 };
    }

    let min = data[0].value;
    let max = data[0].value;

    for (let i = 1; i < data.length; i++) {
      const value = data[i].value;

      if (value < min) {
        min = value;
      }

      if (value > max) {
        max = value;
      }
    }

    return { min, max };
  }, [data]);

  return (
    <>
      <Map
        gradient={[
          theme.colors.blue[9],
          theme.colors.green[2],
          theme.colors.red[9],
        ]}
        getValue={(countryIso) => mapData?.[countryIso]?.[selectedDate]}
        onCountrySelect={onCountrySelect}
        minValue={min}
        maxValue={max}
      />
    </>
  );
}

export default MapArea;
