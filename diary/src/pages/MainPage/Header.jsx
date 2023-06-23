import moment from "moment";
import { useState, useCallback, useEffect, useMemo } from "react";
import { Text, Select, Flex, Box, Title } from "@mantine/core";
import { MonthPickerInput, YearPickerInput } from "@mantine/dates";

import { getMeasurements, getEarliest, getLatest } from "../../utils/api";
import { measurementOptions } from "../../utils/measurements";

function Header({
  measurement,
  onMeasurementChange,
  dateRange,
  onDateRangeChange,
  selectedDate,
  setSelectedDate,
  interval,
  showDate,
}) {
  const [measurements, setMeasurements] = useState([]);
  const [availableDateRange, setAvailableDateRange] = useState({
    from: null,
    to: null,
  });

  useEffect(() => {
    setSelectedDate(dateRange.from);
  }, [dateRange]);

  const DatePickerComponent = useMemo(() => {
    switch (interval) {
      case "month":
        return MonthPickerInput;
      default:
        return YearPickerInput;
    }
  }, [interval]);

  const displayDate = useMemo(() => {
    if (!selectedDate) {
      return "";
    } else {
      return moment(selectedDate).format(
        interval === "month" ? "MMMM YYYY" : "YYYY"
      );
    }
  }, [interval, selectedDate]);

  const fetchMeasurements = useCallback(async () => {
    const data = await getMeasurements();
    const options = measurementOptions.filter((option) =>
      data.includes(option.value)
    );
    setMeasurements(options);
    const defaultMeasurement = options.find((m) => m.default);
    onMeasurementChange(
      defaultMeasurement ? defaultMeasurement.value : options[0].value
    );
  }, []);

  const fetchAvailableDateRange = useCallback(async () => {
    const [fromTimestamp, toTimestamp] = await Promise.all([
      getEarliest(),
      getLatest(),
    ]);
    const from = moment(fromTimestamp).format("YYYY-MM-DD");
    const to = moment(toTimestamp).format("YYYY-MM-DD");
    setAvailableDateRange({ from, to });
    onDateRangeChange({ from, to });
  }, []);

  useEffect(() => {
    fetchMeasurements();
    fetchAvailableDateRange();
  }, []);

  return (
    <Flex
      justify="center"
      sx={(theme) => ({
        paddingLeft: theme.spacing.md,
        paddingRight: theme.spacing.md,
        paddingTop: theme.spacing.md,
      })}
    >
      <div>
        <Flex gap="md" align="center">
          <Text>Showing</Text>
          <Select
            w={280}
            placeholder="Measurement"
            data={measurements}
            value={measurement}
            onChange={onMeasurementChange}
          />
          <Text>From</Text>
          <DatePickerComponent
            w={200}
            placeholder="Starting Date"
            value={new Date(dateRange.from)}
            onChange={(value) =>
              onDateRangeChange((dates) => ({
                ...dates,
                from: moment(value).format("YYYY-MM-DD"),
              }))
            }
            minDate={new Date(availableDateRange.from)}
            maxDate={new Date(availableDateRange.to)}
          />
          <Text>To: </Text>
          <DatePickerComponent
            w={200}
            placeholder="End Date"
            value={new Date(dateRange.to)}
            onChange={(value) =>
              onDateRangeChange((dates) => ({
                ...dates,
                to: moment(value).format("YYYY-MM-DD"),
              }))
            }
            minDate={new Date(availableDateRange.from)}
            maxDate={new Date(availableDateRange.to)}
          />
        </Flex>
        {showDate && (
          <Flex
            justify="center"
            sx={(theme) => ({ paddingTop: theme.spacing.md })}
          >
            <Title order={2}>{displayDate}</Title>
          </Flex>
        )}
      </div>
    </Flex>
  );
}

export default Header;
