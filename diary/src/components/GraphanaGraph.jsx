import moment from "moment";
import { useMantineTheme } from "@mantine/core";

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL;

function convertTime(dateString) {
  const date = moment.utc(dateString, "YYYY-MM-DD");
  const timestamp = date.valueOf();
  return timestamp;
}

function GraphanaGraph({
  countryId,
  width = 790,
  height = 300,
  from,
  to,
  panelId,
}) {
  const { colorScheme } = useMantineTheme();
  return (
    <iframe
      src={`${GRAFANA_URL}d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertTime(
        from
      )}&to=${convertTime(
        to
      )}&var-country_id=${countryId}&theme=${colorScheme}&panelId=${panelId}&kiosk`}
      width={width}
      height={height}
      frameBorder="0"
    />
  );
}
export default GraphanaGraph;
