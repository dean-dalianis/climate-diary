import moment from 'moment';
import {useCallback, useEffect, useMemo, useState} from 'react';
import {AppShell, Group, Header, LoadingOverlay, Select, Skeleton} from '@mantine/core';

import DarkModeSwitch from './components/DarkModeSwitch';
import DateSlider from './components/DateSlider';
import Map from './components/Map';
import PlayButton from './components/PlayButton';
import {
    getAnalysis,
    getEarliest,
    getGsom,
    getLatest,
    getMaximumTemperature,
    getMeasurements,
    getMinimumTemperature
} from "./utils/api";

const measurementOptions = [
    {
        value: "Average_Temperature_decadal_average",
        label: "Average Temperature by decade",
        interval: "decade",
        default: true
    },
    {
        value: "Maximum_Temperature_decadal_average",
        label: "Maximum Temperature by decade",
        interval: "decade",
    },
    {
        value: "Minimum_Temperature_decadal_average",
        label: "Minimum Temperature by decade",
        interval: "decade",
    },
    {
        value: "Extreme_Maximum_Temperature_decadal_average",
        label: "Extreme Maximum Temperature by decade",
        interval: "decade",
    },
    {
        value: "Extreme_Minimum_Temperature_decadal_average",
        label: "Extreme Minimum Temperature by decade",
        interval: "decade",
    },
    {
        value: "Average_Temperature_yearly_average",
        label: "Average Temperature by year",
        interval: "year"
    },
    {
        value: "Maximum_Temperature_yearly_average",
        label: "Maximum Temperature by year",
        interval: "year"
    },
    {
        value: "Minimum_Temperature_yearly_average",
        label: "Minimum Temperature by year",
        interval: "year"

    },
    {
        value: "Extreme_Maximum_Temperature_yearly_average",
        label: "Extreme Maximum Temperature by year",
        interval: "year"

    },
    {
        value: "Extreme_Minimum_Temperature_yearly_average",
        label: "Extreme Minimum Temperature by year",
        interval: "year"
    },
    {
        value: "Average_Temperature",
        label: "Average Temperature",
        interval: "year"
    }
];

function App() {
    const [measurements, setMeasurements] = useState([]);
    const [availableDateRange, setAvailableDateRange] = useState({
        from: null,
        to: null,
    });
    const [loadingOptions, setLoadingOptions] = useState(false);

    const [data, setData] = useState([]);
    const [loadingData, setLoadingData] = useState(false);

    const [error, setError] = useState(null);

    const [selectedDateRange, setSelectedDateRange] = useState({
        from: null,
        to: null,
    });

    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedMeasurement, setSelectedMeasurement] = useState(null);
    const [maximumTemperature, setMaximumTemperature] = useState(null);
    const [minimumTemperature, setMinimumTemperature] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const handleAnimationButtonClick = (date) => {
        if (!isPlaying && date) {
            setSelectedDate(date);
        }
        setIsPlaying(!isPlaying);
    };

    const fetchMeasurements = useCallback(async () => {
        const data = await getMeasurements();
        const options = measurementOptions.filter((option) =>
            data.includes(option.value)
        );
        setMeasurements(options);
        const defaultMeasurement = options.find((m) => m.default);
        setSelectedMeasurement(
            defaultMeasurement ? defaultMeasurement.value : options[0].value
        );
    }, []);

    const fetchMinMaxTemperature = useCallback(async () => {
        const [maxTemp, minTemp] = await Promise.all([getMaximumTemperature(selectedMeasurement), getMinimumTemperature(selectedMeasurement)]);
        setMaximumTemperature(maxTemp);
        setMinimumTemperature(minTemp);
    }, [selectedMeasurement]);

    const fetchAvailableDateRange = useCallback(async () => {
        const [fromTimestamp, toTimestamp] = await Promise.all([getEarliest(), getLatest(),]);
        const from = moment(fromTimestamp).format("YYYY-MM-DD");
        const to = moment(toTimestamp).format("YYYY-MM-DD");
        setAvailableDateRange({from, to});
        setSelectedDateRange({from, to});
        setSelectedDate(from);
    }, []);

    const fetchOptions = useCallback(async () => {
        try {
            setLoadingOptions(true);
            await Promise.all([fetchAvailableDateRange(), fetchMeasurements()]);
        } catch (error) {
            setError(error);
        } finally {
            setLoadingOptions(false);
        }
    }, []);

    useEffect(() => {
        fetchOptions();
    }, []);

    const fetchData = useCallback(async () => {
        try {
            setLoadingData(true);
            let data;
            // TODO: If need to use GSOM measurements, create a list with GSOM measurements in order to use the correct endpoint if the selected measurement is a GSOM measurement
            if (selectedMeasurement === "Average_Temperature") {
                data = await getGsom({
                    measurement: selectedMeasurement,
                    start_date: selectedDateRange.from,
                    end_date: selectedDateRange.to
                });
            } else {
                data = await getAnalysis({
                    measurement: selectedMeasurement,
                    start_date: selectedDateRange.from,
                    end_date: selectedDateRange.to,
                });
            }
            setData(data);
        } catch (error) {
            setError(error);
        } finally {
            setLoadingData(false);
        }
    });

    useEffect(() => {
        if (selectedMeasurement || selectedDateRange.from || selectedDateRange.to) {
            fetchData();
        }
    }, [selectedDateRange, selectedMeasurement]);

    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, []);

    useEffect(() => {
        if (selectedMeasurement) fetchMinMaxTemperature();
    }, [selectedMeasurement]);

    const dates = useMemo(
        () => [...new Set(data.map(({time}) => time))].map((time) => moment(time).format('YYYY-MM-DD')),
        [data]
    );

    useEffect(() => {
        if (isPlaying) {
            const currentIndex = dates.indexOf(selectedDate);
            if (currentIndex < dates.length - 1) {
                const delay = 10000 / dates.length;
                const timeoutId = setTimeout(() => setSelectedDate(dates[currentIndex + 1]), delay);
                return () => clearTimeout(timeoutId);
            } else {
                setIsPlaying(false);
            }
        }
    }, [selectedDate, isPlaying, dates]);

    return (
        <>
            <div style={{position: 'relative', height: '100vh'}}>
                <LoadingOverlay visible={loadingOptions} overlayBlur={2}/>

                <Header height={80} style={{position: 'fixed', top: 0, width: '100%', zIndex: 2}}>
                    <Group sx={{height: '100%'}} px={20}>
                        <DateSlider selectedDate={selectedDate} dates={dates} onChange={setSelectedDate}/>
                        <PlayButton
                            isPlaying={isPlaying}
                            selectedDate={selectedDate}
                            dates={dates}
                            handleAnimationButtonClick={handleAnimationButtonClick}
                        />
                        <Select
                            data={measurements}
                            value={selectedMeasurement}
                            onChange={setSelectedMeasurement}
                            placeholder="Measurement"
                            sx={{
                                minWidth: '250px',
                            }}
                        />
                        <DarkModeSwitch/>
                    </Group>
                    {loadingData && <Skeleton height={4} radius="xl"/>}
                </Header>

                <div style={{paddingTop: 80}}>
                    <AppShell padding="0">
                        <Map
                            data={data}
                            selectedDate={selectedDate}
                            minTemperature={minimumTemperature}
                            maxTemperature={maximumTemperature}
                        />
                    </AppShell>
                </div>
            </div>
        </>
    );
}

export default App;
