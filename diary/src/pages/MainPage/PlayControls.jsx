import { useState, useEffect } from "react";
import { Flex, Paper, Group } from "@mantine/core";
import PlayButton from "../../components/PlayButton";
import DateSlider from "../../components/DateSlider";

function PlayControls({ selectedDate, setSelectedDate, dates, interval }) {
  const [isPlaying, setIsPlaying] = useState(false);

  const handleAnimationButtonClick = (date) => {
    if (!isPlaying && date) {
      setSelectedDate(date);
    }
    setIsPlaying(!isPlaying);
  };

  useEffect(() => {
    if (isPlaying) {
      const currentIndex = dates.indexOf(selectedDate);
      if (currentIndex < dates.length - 1) {
        const delay = 10000 / dates.length;
        const timeoutId = setTimeout(
          () => setSelectedDate(dates[currentIndex + 1]),
          delay
        );
        return () => clearTimeout(timeoutId);
      } else {
        setIsPlaying(false);
      }
    }
  }, [selectedDate, isPlaying, dates]);

  return (
    <Flex
      justify="center"
      sx={(theme) => ({
        paddingBottom: theme.spacing.md,
      })}
    >
      <Paper shadow="sm" radius="xl" p="md" w={800}>
        <Group align="center">
          <PlayButton
            isPlaying={isPlaying}
            selectedDate={selectedDate}
            dates={dates}
            handleAnimationButtonClick={handleAnimationButtonClick}
          />
          <DateSlider
            selectedDate={selectedDate}
            dates={dates}
            onChange={setSelectedDate}
            interval={interval}
          />
        </Group>
      </Paper>
    </Flex>
  );
}

export default PlayControls;
