import moment from "moment";
import {useMemo} from "react";
import {Slider, Text} from "@mantine/core";

function DateSlider({selectedDate, dates, onChange}) {
    const displayDate = useMemo(
        () => (selectedDate ? moment(selectedDate).format("MMM YYYY") : "-"),
        [selectedDate]
    );
    const sliderValue = useMemo(
        () => (selectedDate ? dates.indexOf(selectedDate) : 0),
        [selectedDate, dates]
    );

    const sliderMax = useMemo(
        () => (selectedDate ? dates.length - 1 : 10),
        [selectedDate, dates]
    );

    const sliderMarks = useMemo(() => {
        if (dates.length < 5) return [];
        const percentiles = [0, 25, 50, 75, 100];
        const roundedPercentiles = percentiles.map((percentile) =>
            Math.round((percentile / 100) * sliderMax)
        );
        return roundedPercentiles.map((value) => ({
            value,
            label: moment(dates[value]).format("YYYY-MM"),
        }));
    });

    const updateDate = (value) => {
        onChange(dates[value]);
    };

    return (
        <>
            <Text sx={{minWidth: "80px"}}>{displayDate}</Text>
            <Slider
                value={sliderValue}
                onChange={updateDate}
                min={0}
                max={sliderMax}
                size="lg"
                thumbSize={14}
                label={null}
                marks={sliderMarks}
                sx={({spacing}) => ({
                    flexGrow: 1,
                    marginLeft: spacing.xs,
                    marginRight: spacing.xs,
                })}
                styles={({fontSizes}) => ({markLabel: {fontSize: fontSizes.xs}})}
            />
        </>
    );
}

export default DateSlider;
