import React, {useState} from 'react';
import {ComposableMap, Geographies, Geography} from 'react-simple-maps';
import Modal from 'react-modal';
import {CountryDetailsModal} from "./CountryDetailsModal";

const geoUrl = "https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries.json";

Modal.setAppElement('#root'); // replace '#root' with the id of your app's root element


const MapChart = ({data, selectedDates}) => {
    const [selectedCountry, setSelectedCountry] = useState(null);
    const [modalIsOpen, setIsOpen] = useState(false);

    // Aggregate data by country and time
    const aggregatedData = data.reduce((acc, d) => {
        const year = new Date(d.time).getFullYear();
        const month = new Date(d.time).getMonth() + 1;
        if ((year > selectedDates[0].year || (year === selectedDates[0].year && month >= selectedDates[0].month)) &&
            (year < selectedDates[1].year || (year === selectedDates[1].year && month <= selectedDates[1].month))) {
            if (!acc[d.fields.country_id]) {
                acc[d.fields.country_id] = {
                    count: 0,
                    total: 0,
                    countryName: d.fields.country_name
                };
            }
            acc[d.fields.country_id].count++;
            acc[d.fields.country_id].total += d.fields.value;
        }
        return acc;
    }, {});

    const openModal = () => {
        setIsOpen(true);
    }

    const closeModal = () => {
        setIsOpen(false);
    }

    return (
        <div>
            <ComposableMap>
                <Geographies geography={geoUrl}>
                    {({geographies}) =>
                        geographies.map(geo => {
                            const countryData = aggregatedData[geo.properties['Alpha-2']];
                            return (
                                <Geography
                                    key={geo.rsmKey}
                                    geography={geo}
                                    fill={countryData ? getColorForTemperature(countryData.total / countryData.count) : "#EEE"}
                                    onClick={() => {
                                        setSelectedCountry(countryData);
                                        openModal();
                                    }}
                                />
                            );
                        })
                    }
                </Geographies>
            </ComposableMap>
            <CountryDetailsModal open={modalIsOpen} onRequestClose={closeModal} selectedCountry={selectedCountry}/>
        </div>
    );
};

// This function returns a color based on the temperature value
function getColorForTemperature(value) {
    if (value < 10) {
        return "#6495ED"; // Cold temperature
    } else if (value < 20) {
        return "#7FFFD4"; // Mild temperature
    } else {
        return "#FF6347"; // Hot temperature
    }
}

export default MapChart;
