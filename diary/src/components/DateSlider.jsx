import moment from "moment";
import { useMemo } from "react";
import { Slider, Text } from "@mantine/core";

function DateSlider({ selectedDate, dates, onChange, interval }) {
  const sliderValue = useMemo(
    () => (selectedDate ? dates.indexOf(selectedDate) : 0),
    [selectedDate, dates]
  );

  const sliderMax = useMemo(
    () => (selectedDate ? dates.length - 1 : 10),
    [selectedDate, dates]
  );

  const updateDate = (value) => {
    onChange(dates[value]);
  };

  const currDate = useMemo(
    () =>
      dates && dates.length > 0
        ? moment(selectedDate).format(interval === "month" ? "MM/YYYY" : "YYYY")
        : "",
    [selectedDate]
  );
  const maxDate = useMemo(
    () =>
      dates && dates.length > 1
        ? moment(dates[dates.length - 1]).format(
            interval === "month" ? "MM/YYYY" : "YYYY"
          )
        : "",
    [dates]
  );
  return (
    <>
      <Text fz="xs">{currDate}</Text>
      <Slider
        color="red"
        value={sliderValue}
        onChange={updateDate}
        min={0}
        max={sliderMax}
        size="lg"
        thumbSize={14}
        label={null}
        sx={({ spacing }) => ({
          flexGrow: 1,
          marginLeft: spacing.xs,
          marginRight: spacing.xs,
        })}
        styles={({ fontSizes }) => ({ markLabel: { fontSize: fontSizes.xs } })}
      />
      <Text fz="xs">{maxDate}</Text>
    </>
  );
}

export default DateSlider;
