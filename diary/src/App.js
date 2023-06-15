import React, {useState} from 'react';
import MapChart from './MapChart';
import TimeSlider from './TimeSlider';
import {generateRandomData} from './TestBoundingBoxes';

const data = generateRandomData();


function App() {
    const [selectedDates, setSelectedDates] = useState([
        {year: 1880, month: 1},
        {year: new Date().getFullYear(), month: new Date().getMonth() + 1}
    ]);

    const handleTimeChange = (newDates) => {
        setSelectedDates(newDates);
    };

    return (
        <div className="App" id="root">
            <TimeSlider onChange={handleTimeChange}/>
            <MapChart data={data} selectedDates={selectedDates}/>
        </div>
    );
}

export default App;