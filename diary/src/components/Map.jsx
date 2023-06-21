import React, {useEffect, useMemo, useRef, useState} from 'react';
import {GeoJSON, MapContainer, TileLayer} from 'react-leaflet';
import {Box, ColorSwatch, Group, Modal, Stack, Text} from '@mantine/core';
import 'leaflet/dist/leaflet.css';
import moment from 'moment';
import {scaleLinear} from 'd3-scale';
import {interpolateRgb} from 'd3-interpolate';
import {getCountryFromCoordinates} from "../utils/api";
import countriesJson from '../map.json';


function convertDateToGrafanaTime(dateString) {
    const date = moment.utc(dateString, 'YYYY-MM-DD');
    const timestamp = date.valueOf();
    return timestamp;
}

function MapWrapper({data, selectedDate, minTemperature, maxTemperature}) {
    const [geoJsonData, setGeoJsonData] = useState(null);
    const [mapData, setMapData] = useState({});
    const [selectedCountryCode, setSelectedCountryCode] = useState(null);
    const [selectedCountryName, setSelectedCountryName] = useState(null);
    const ref = useRef(null);

    const getColorForTemperature = (temp) => {
        const colorScale = scaleLinear()
            .domain([minTemperature, (minTemperature + maxTemperature) / 2, maxTemperature])
            .range(['#80adf1', '#73ff00', '#ff0000'])
            .interpolate(interpolateRgb);
        return colorScale(temp);
    };

    useEffect(() => {
        // Set the GeoJSON data from the local file
        setGeoJsonData(countriesJson);

        const mapData = {};
        if (!data) return mapData;

        for (const row of data) {
            // const countryId = getCountryCodeFromName(row.country_name)
            const countryName = row.country_name;

            // console.log(countryId, countryName)

            // if (!mapData[countryId]) {
            //     mapData[countryId] = {};
            // }
            // mapData[countryId][moment(row.time).format("YYYY-MM-DD")] = row.value;

            if (!mapData[countryName]) {
                mapData[countryName] = {};
            }
            mapData[countryName][moment(row.time).format("YYYY-MM-DD")] = row.value;

        }
        setMapData(mapData);
    }, [data]);

    const style = (feature) => {
        // const countryId = feature.properties['ISO_A2'];
        const countryName = feature.properties['ADMIN'];

        const avgTemp =
            // mapData?.[countryId]?.[selectedDate] ||
            mapData?.[countryName]?.[selectedDate];
        if (!avgTemp) {
            console.log('no data for', countryName, selectedDate)
        }
        return {
            fillColor: avgTemp ? getColorForTemperature(avgTemp) : 'transparent',
            weight: 2,
            opacity: 1,
            color: 'white',
            fillOpacity: 0.7,
        };
    };

    const temperatureRange = useMemo(() => {
        const range = [];
        for (let temp = Math.floor(minTemperature / 10) * 10; temp <= maxTemperature; temp += 10) {
            range.push(temp);
        }
        return range.reverse();
    }, [minTemperature, maxTemperature]);

    const handleCountryClick = async (event) => {
        const lat = event.latlng.lat;
        const lng = event.latlng.lng;
        const countryInfo = await getCountryFromCoordinates(lat, lng);

        if (countryInfo) {
            setSelectedCountryCode(countryInfo.countryCode.toUpperCase());
            setSelectedCountryName(countryInfo.countryName);
        }
    };
    const handleCloseModal = () => {
        setSelectedCountryCode(null);
        setSelectedCountryName(null);
    };

    return (
        <div style={{position: 'relative', width: '100%', height: '100%'}}>
            <MapContainer
                center={[51.505, -0.09]}
                zoom={3}
                style={{height: '100vh', width: '100%', position: 'relative', zIndex: 1}}
                worldCopyJump={true}
                maxBounds={[[-90, -180], [90, 180]]}
                maxBoundsViscosity={1.0}
                minZoom={3}
                maxZoom={10}
            >
                <TileLayer
                    attribution='&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {geoJsonData && (
                    <GeoJSON style={style} data={geoJsonData} eventHandlers={{click: handleCountryClick}}/>
                )}
            </MapContainer>

            <Box
                sx={(theme) => ({
                    width: '200px',
                    position: 'absolute',
                    zIndex: 10,
                    bottom: 0,
                    left: 0,
                    padding: theme.spacing.md,
                    marginLeft: theme.spacing.lg,
                    marginBottom: theme.spacing.lg,
                })}
            >
                <Stack spacing="md">
                    {temperatureRange.map((temp) => (
                        <Group spacing="md" key={temp}>
                            <ColorSwatch color={getColorForTemperature(temp)}/>
                            <Text fz="md" color="dark.5">
                                {temp} °C
                            </Text>{' '}
                        </Group>
                    ))}
                </Stack>
            </Box>

            <Modal opened={!!selectedCountryName} onClose={handleCloseModal} title={selectedCountryName} centered
                   size='auto'>
                <Modal.Title>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=35&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=36&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=37&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=38&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=39&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=40&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>

                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=41&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=42&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=27&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=44&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=32&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=40&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=33&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>

                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=29&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>

                    <iframe
                        src={`http://localhost:3000/d-solo/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1&from=${convertDateToGrafanaTime(selectedDate)}&var-country_name=${selectedCountryName}&theme=dark&panelId=30&kiosk`}
                        width="650" height="300" frameBorder="0">
                    </iframe>
                </Modal.Title>
            </Modal>
        </div>
    );
}

export default MapWrapper;
