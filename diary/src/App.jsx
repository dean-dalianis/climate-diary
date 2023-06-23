import { useDisclosure } from "@mantine/hooks";

import { Route, Routes } from "react-router-dom";
import { Box } from "@mantine/core";
import {
  IconLocationFilled,
  IconMapPinFilled,
  IconChartAreaFilled,
  IconMushroomFilled,
} from "@tabler/icons-react";

import Menu from "./components/Menu";
import Logo from "./components/Logo";
import DarkModeSwitch from "./components/DarkModeSwitch";

import MainPage from "./pages/MainPage";
import OtherPage from "./pages/OtherPage";

function App() {
  const [opened, { open, close }] = useDisclosure(false);

  return (
    <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
      <Box
        sx={(theme) => ({
          position: "absolute",
          top: 0,
          left: 0,
          marginTop: theme.spacing.md,
          marginLeft: theme.spacing.md,
          zIndex: 220,
        })}
      >
        <Logo onClick={open} />
      </Box>
      <Box
        sx={(theme) => ({
          position: "absolute",
          top: 0,
          right: 0,
          marginTop: theme.spacing.md,
          marginRight: theme.spacing.md,
          zIndex: 220,
        })}
      >
        <DarkModeSwitch />
      </Box>

      <Menu
        opened={opened}
        close={close}
        links={[
          { label: "Global Map", path: "/", Icon: IconLocationFilled },
          { label: "Other Page", path: "/other", Icon: IconMapPinFilled },
          { label: "Emmissions", Icon: IconChartAreaFilled },
          { label: "Precipitation", Icon: IconMushroomFilled },
        ]}
      />
      <Routes>
        <Route path="/" element={<MainPage />}></Route>
        <Route path="/other" element={<OtherPage />}></Route>
      </Routes>
    </div>
  );
}

export default App;
