export function generateRandomData() {
    const countryCodes = [
        "AL", "AN", "AU", "BO", "BE", "BU", "HR", "CY", "EZ", "DA", "EN", "FI", "FR", "GM", "GR", "HU",
        "IC", "EI", "IT", "KV", "LG", "LH", "LU", "MK", "MT", "MD", "MN", "NL", "NO", "PL", "PO", "RO",
        "RI", "LO", "SI", "SP", "SW", "SZ", "UK", "UP", "RS", "BO", "MD", "SM", "IM", "LI", "MC", "VA"
    ];
    const measurements = ["Average_Temperature", "Maximum_Temperature", "Minimum_Temperature"];
    const data = [];

    for (const countryCode of countryCodes) {
        const numStations = Math.floor(Math.random() * 3) + 3;

        for (let i = 0; i < numStations; i++) {
            const station = `GHCND:${countryCode}000${i}`;
            const latitude = Math.random();
            const longitude = Math.random();
            const elevation = Math.random() * 2000;
            for (let j = 0; j < 5; j++) {
                const year = Math.floor(Math.random() * (new Date().getFullYear() - 1880 + 1)) + 1880;
                const month = Math.floor(Math.random() * 12) + 1;
                const time = `${year}-${month < 10 ? '0' : ''}${month}-15T00:00:00Z`;
                const value = Math.random() * 40 - 10;
                const yoyChange = Math.random() * 2 - 1;
                const dodChange = Math.random() * 2 - 1;
                const decadalAverageTemperature = value + Math.random() * 2 - 1;
                const daysMissing = Math.floor(Math.random() * 10);
                const sourceCode = String.fromCharCode(Math.floor(Math.random() * 26) + 65);
                for (const measurement of measurements) {
                    data.push({
                        measurement,
                        tags: {
                            country: countryCode
                        },
                        time,
                        fields: {
                            value,
                            country_id: countryCode,
                            station,
                            latitude,
                            longitude,
                            elevation,
                            yoy_change: yoyChange,
                            dod_change: dodChange,
                            decadal_average_temperature: decadalAverageTemperature,
                            days_missing: daysMissing,
                            source_code: sourceCode
                        }
                    });
                }
            }
        }
    }

    return data;
}
