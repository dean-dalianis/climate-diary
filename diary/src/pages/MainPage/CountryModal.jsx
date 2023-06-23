import { useEffect, useState } from "react";
import {
  Overlay,
  Box,
  Title,
  ScrollArea,
  Flex,
  Tabs,
  ActionIcon,
} from "@mantine/core";
import axios from "axios";

import { IconX } from "@tabler/icons-react";

import GraphanaGraph from "../../components/GraphanaGraph";

const graphs = [
  { group: "Temprature", panels: [35, 36, 37] },
  { group: "Percipitation", panels: [35, 36, 37] },
  { group: "Other", panels: [35, 36, 37] },
];

function CountryModal({ country, dateRange, onClose }) {
  const [flag, setFlag] = useState(null);
  useEffect(() => {
    axios
      .get(`https://restcountries.com/v3.1/alpha/${country.id}`)
      .then((res) => setFlag(res.data[0].flags));
  }, [country.id]);

  return (
    <Overlay blur={15}>
      <Box w={850} h={"100%"} p="lg" sx={{ margin: "auto" }}>
        <Flex
          justify="space-between"
          align="center"
          sx={(theme) => ({
            marginTop: "80px",
            marginBottom: theme.spacing.lg,
          })}
        >
          <Flex gap="md" align="center">
            {flag && (
              <img width={50} height={32} src={flag.png} alt={flag.alt} />
            )}

            <Title>{country.name}</Title>
          </Flex>

          <ActionIcon onClick={onClose} size={36}>
            <IconX size="2rem" />
          </ActionIcon>
        </Flex>
        <Tabs color="teal" defaultValue={graphs[0].group}>
          <Tabs.List>
            {graphs.map(({ group }) => (
              <Tabs.Tab key={group} value={group}>
                {group}
              </Tabs.Tab>
            ))}
          </Tabs.List>
          <ScrollArea h={700}>
            {graphs.map(({ group, panels }) => (
              <Tabs.Panel key={group} value={group} pt="xs">
                {panels.map((id) => (
                  <div key={id} style={{ marginBottom: "16px" }}>
                    <GraphanaGraph
                      country={country.id}
                      from={dateRange.from}
                      to={dateRange.to}
                      panelId={id}
                    />
                  </div>
                ))}
              </Tabs.Panel>
            ))}
          </ScrollArea>
        </Tabs>
      </Box>
    </Overlay>
  );
}

export default CountryModal;
