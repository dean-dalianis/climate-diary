import React from 'react';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import ReplayIcon from '@mui/icons-material/Replay';

function PlayButton({ isPlaying, selectedDate, dates, handleAnimationButtonClick }) {
  const handleButtonClick = () => {
    if (!isPlaying && selectedDate === dates[dates.length - 1]) {
      handleAnimationButtonClick(dates[0]);
    } else {
      handleAnimationButtonClick();
    }
  };

  return (
    <button onClick={handleButtonClick}>
      {isPlaying ? (
        <PauseIcon />
      ) : selectedDate === dates[dates.length - 1] ? (
        <ReplayIcon />
      ) : (
        <PlayArrowIcon />
      )}
    </button>
  );
}

export default PlayButton;
