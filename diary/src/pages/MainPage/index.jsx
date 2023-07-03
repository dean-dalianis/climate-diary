import moment from "moment";
import {useCallback, useEffect, useMemo, useState} from "react";

import {getGsoy} from "../../utils/api";
import {measurementOptions} from "../../utils/measurements";

import {LoadingOverlay} from "@mantine/core";
import MapArea from "./MapArea";
import Header from "./Header";
import PlayControls from "./PlayControls";
import CountryModal from "./CountryModal";

function MainPage() {
    const [data, setData] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [measurement, setMeasurement] = useState(null);
    const [selectedCountry, setSelectedCountry] = useState(null);
    const [dateRange, setDateRange] = useState({
        from: null,
        to: null,
    });

    const [isFetching, setIsFetching] = useState(false);
    const showSpinner = useMemo(() => {
        if (isFetching) return true;
        if ((!data || data.length === 0) && !selectedCountry) return true;
        return false;
    }, [data, isFetching]);

    const fetchData = useCallback(async () => {
        setIsFetching(true);
        let data;
        const params = {
            measurement: measurement,
            start_date: dateRange.from,
            end_date: dateRange.to,
        };
        data = await getGsoy(params);
        setData(data);
        setIsFetching(false);
    });

    useEffect(() => {
        if (measurement && dateRange.from && dateRange.to) {
            fetchData();
        }
    }, [dateRange, measurement]);

    const interval = useMemo(
        () =>
            measurement &&
            measurementOptions.find((option) => option.value === measurement)
                .interval,
        [measurement]
    );

    const dates = useMemo(
        () =>
            [...new Set(data.map(({time}) => time))]
                .map((time) => moment(time).format("YYYY-MM-DD"))
                .sort(),
        [data]
    );

    // TODO : loading overlay throguh context

    return (
        <div
            style={{
                position: "relative",
                width: "100%",
                height: "100%",
            }}
        >
            <div
                style={{
                    position: "absolute",
                    width: "100%",
                    top: 0,
                    zIndex: 210,
                }}
            >
                <Header
                    measurement={measurement}
                    onMeasurementChange={setMeasurement}
                    dateRange={dateRange}
                    onDateRangeChange={setDateRange}
                    selectedDate={selectedDate}
                    setSelectedDate={setSelectedDate}
                    interval={interval}
                    showDate={!selectedCountry}
                />
            </div>
            <div
                style={{
                    position: "absolute",
                    width: "100%",
                    bottom: 0,
                    zIndex: 210,
                }}
            >
                {!selectedCountry && (
                    <PlayControls
                        selectedDate={selectedDate}
                        setSelectedDate={setSelectedDate}
                        dates={dates}
                        interval={interval}
                    />
                )}
            </div>
            <LoadingOverlay visible={showSpinner} overlayBlur={2} zIndex={200}/>
            {selectedCountry && (
                <CountryModal
                    country={selectedCountry}
                    dateRange={dateRange}
                    onClose={() => setSelectedCountry(null)}
                />
            )}
            <MapArea
                data={data}
                selectedDate={selectedDate}
                onCountrySelect={setSelectedCountry}
            />
        </div>
    );
}

export default MainPage;
