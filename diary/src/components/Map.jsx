import moment from "moment";
import {Box, ColorSwatch, Group, Stack, Text, useMantineTheme,} from "@mantine/core";
import {useEffect, useMemo, useRef, useState} from "react";
import {scaleLinear} from 'd3-scale';
import {interpolateRgb} from 'd3-interpolate';

import {ComposableMap, Geographies, Geography, ZoomableGroup,} from "react-simple-maps";

const geoUrl =
    "https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries.json";

const initalZoomParams = {
    center: [9.502771447726788, 25.100818733935455],
    zoom: 2.002266295581086,
};

function MapWrapper({data, selectedDate, minTemperature, maxTemperature}) {
    for (const row of data) {
        if (row.country_name === "France") {
            console.log('heyy');
        }
    }
    const {colorScheme, colors} = useMantineTheme();

    const getColorForTemperature = (temp, minTemperature, maxTemperature) => {
        const colorScale = scaleLinear()
            .domain([minTemperature, (minTemperature + maxTemperature) / 2, maxTemperature])
            .range(["#80adf1", "#73ff00", "#ff0000"])
            .interpolate(interpolateRgb);
        return colorScale(temp);
    };


    const geographyTheme = useMemo(() => {
        if (colorScheme === "light") {
            return {
                fill: colors.gray[3],
                stroke: colors.gray[5],
            };
        } else {
            return {
                fill: colors.dark[5],
                stroke: colors.dark[7],
            };
        }
    }, [colorScheme]);

    const [height, setHeight] = useState(0);
    const [width, setWidth] = useState(0);
    const [zoomParams, setZoomParams] = useState({});
    const ref = useRef(null);

    useEffect(() => {
        setHeight(ref.current.clientHeight);
        setWidth(ref.current.clientWidth);
        setZoomParams(initalZoomParams);
    }, []);

    const mapData = useMemo(() => {
        const mapData = {};
        if (!data) return mapData;

        for (const row of data) {
            if (!mapData[row.country_name]) {
                mapData[row.country_name] = {};
            }
            mapData[row.country_name][moment(row.time).format("YYYY-MM-DD")] =
                row.value;
        }
        return mapData;
    }, [data]);

    return (
        <div
            ref={ref}
            style={{
                width: "100%",
                height: "calc(100% - 10px)",
                position: "relative",
            }}
        >
            <Box
                sx={(theme) => ({
                    width: "200px",
                    position: "absolute",
                    bottom: 0,
                    left: 0,
                    padding: theme.spacing.md,
                    marginLeft: theme.spacing.lg,
                    marginBottom: theme.spacing.lg,
                })}
            >
                <Stack spacing="md">
                    {Array.from({length: Math.ceil((maxTemperature - Math.floor(minTemperature / 10) * 10) / 10) + 1}, (_, i) => Math.floor(minTemperature / 10) * 10 + i * 10).reverse().map((temp) => (
                        <Group spacing="md">
                            <ColorSwatch color={getColorForTemperature(temp, minTemperature, maxTemperature)}/>
                            <Text fz="md">{temp} °C </Text>
                        </Group>
                    ))}
                </Stack>

            </Box>
            <ComposableMap width={width} height={height} projection="geoMercator" projectionConfig={{
                rotate: [0.0, -53.0, 0],
                scale: 200,
            }}>
                <ZoomableGroup {...zoomParams}>
                    <Geographies geography={geoUrl}>
                        {({geographies}) =>
                            geographies.map((geo) => {
                                const country = geo.properties.name;
                                // console.log(country);
                                const avgTemp = mapData?.[country]?.[selectedDate];

                                return (
                                    <Geography
                                        key={geo.rsmKey}
                                        geography={geo}
                                        fill={avgTemp ? getColorForTemperature(avgTemp, minTemperature, maxTemperature) : geographyTheme.fill}
                                        stroke={geographyTheme.stroke}
                                        style={{
                                            default: {outline: "stroke"},
                                            hover: {
                                                outline: "stroke",
                                                cursor: "pointer",
                                            },
                                            pressed: {outline: "none"},
                                        }}
                                        onClick={(e) => console.log(e)}
                                    />
                                );
                            })
                        }
                    </Geographies>
                </ZoomableGroup>
            </ComposableMap>
        </div>
    );
}

export default MapWrapper;
