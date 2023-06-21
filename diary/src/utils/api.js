import axios from "axios";
import {notifications} from "@mantine/notifications";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

// Add a request interceptor
api.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        console.log("Request error:", error);
        return Promise.reject(error);
    }
);

// Add a response interceptor
api.interceptors.response.use(
    (response) => {
        // Modify response data if needed
        return response;
    },
    (error) => {
        console.log({error});
        const {message} = error;
        notifications.show({
            color: "red",
            title: "Error",
            message: message || "Something went wrong!",
        });
        return Promise.reject(error);
    }
);

export const getCountries = async () => {
    const data = await api.get("/diary/other/countries").then((res) => res.data);
    return data;
};

export const getEarliest = async () => {
    const data = await api.get("/diary/other/earliest").then((res) => res.data);
    return data;
};

export const getLatest = async () => {
    const data = await api.get("/diary/other/latest").then((res) => res.data);
    return data;
};

export const getMeasurements = async () => {
    const data = await api
        .get("/diary/other/measurements/")
        .then((res) => res.data);
    return data;
};

export const getMaximumTemperature = async (measurement) => {
    const data = await api
        .get(`/diary/other/temperature/maximum/${measurement}`)
        .then((res) => res.data);
    return data;
};


export const getMinimumTemperature = async (measurement) => {
    const data = await api
        .get(`/diary/other/temperature/minimum/${measurement}`)
        .then((res) => res.data);
    return data;
};


export const getAnalysis = async (params) => {
    const data = await api
        .get("/diary/analysis/data", {params})
        .then((res) => res.data);
    return data;
};

export const getGsom = async (params) => {
    const data = await api
        .get("/diary/gsom/data", {params})
        .then((res) => res.data);
    return data;
};

export const getCountryFromCoordinates = async (lat, lng) => {
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`;

    try {
        const response = await axios.get(url);
        const {country_code, country} = response.data.address;
        return {countryCode: country_code, countryName: country};
    } catch (error) {
        console.error('Error fetching country information:', error);
        return null;
    }
};

export const getCountryCodeFromName = async (countryName) => {
    const url = `https://api.restcountries.com/v3.1/name/${countryName}`;

    try {
        const response = await axios.get(url);
        const countryCode = response.data[0]['tld']['cca2'];
        return countryCode;
    } catch (error) {
        console.error('Error fetching country information:', error);
        return null;
    }
};


