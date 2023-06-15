import React, {useState} from 'react';
import ReactSlider from 'react-slider';
import styled from 'styled-components';

const StyledSlider = styled(ReactSlider)`
  width: 100%;
  height: 25px;
`;

const StyledThumb = styled.div`
  height: 25px;
  line-height: 25px;
  width: 25px;
  text-align: center;
  background-color: #4CAF50;
  color: #fff;
  border-radius: 50%;
  cursor: grab;
`;

const Thumb = (props, state) =>
    <StyledThumb {...props}>{Math.floor(state.valueNow / 12)}-{state.valueNow % 12 || 12}</StyledThumb>;

const StyledTrack = styled.div`
  top: 0;
  bottom: 0;
  background: ${props => props.index === 2 ? '#ddd' : '#4CAF50'};
  border-radius: 999px;
`;

const Track = (props, state) => <StyledTrack {...props} index={state.index}/>;

const TimeSlider = ({onChange}) => {
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth() + 1;
    const [selectedDates, setSelectedDates] = useState([1880 * 12 + 1, currentYear * 12 + currentMonth]);

    const handleSliderChange = (newValues) => {
        setSelectedDates(newValues);
        onChange(newValues.map(value => ({
            year: Math.floor(value / 12),
            month: value % 12 || 12
        })));
    };

    return (
        <StyledSlider
            min={1880 * 12 + 1}
            max={currentYear * 12 + currentMonth}
            value={selectedDates}
            onChange={handleSliderChange}
            renderThumb={Thumb}
            renderTrack={Track}
            pearling
            minDistance={12}
        />
    );
};

export default TimeSlider;
