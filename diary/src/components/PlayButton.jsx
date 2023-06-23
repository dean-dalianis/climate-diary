import { ActionIcon } from "@mantine/core";
import {
  IconPlayerPlay,
  IconPlayerPause,
  IconPlayerTrackPrev,
} from "@tabler/icons-react";

function PlayButton({
  isPlaying,
  selectedDate,
  dates,
  handleAnimationButtonClick,
}) {
  const handleButtonClick = () => {
    if (!isPlaying && selectedDate === dates[dates.length - 1]) {
      handleAnimationButtonClick(dates[0]);
    } else {
      handleAnimationButtonClick();
    }
  };

  return (
    <ActionIcon onClick={handleButtonClick} size={36}>
      {isPlaying ? (
        <IconPlayerPause size="1rem" />
      ) : selectedDate === dates[dates.length - 1] ? (
        <IconPlayerTrackPrev size="1rem" />
      ) : (
        <IconPlayerPlay size="1rem" />
      )}
    </ActionIcon>
  );
}

export default PlayButton;
