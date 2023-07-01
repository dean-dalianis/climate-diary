import { useEffect, useState } from "react";
import { ActionIcon, Box, Flex, Overlay, ScrollArea, Tabs, Title } from "@mantine/core";
import axios from "axios";
import { IconX } from "@tabler/icons-react";
import GrafanaPanel from "../../components/GrafanaPanel";

const graphs = [
  { group: "Extreme Temperatures", panels: [57, 61] },
  { group: "Temperatures", panels: [58, 62, 59, 63, 60, 64] },
  { group: "Precipitation", panels: [47, 71, 45, 72, 48, 73] },
  { group: "Snow", panels: [50, 67, 52, 68, 51, 69, 53, 70] },
  { group: "Evaporation", panels: [55, 65, 56, 66] },
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
      <Box w={1800} h={"100%"} p="lg" sx={{ margin: "auto" }}>
        <Flex
          justify="space-between"
          align="center"
          sx={(theme) => ({
            marginTop: "80px",
            marginBottom: theme.spacing.lg,
          })}
        >
          <Flex gap="md" align="center">
            {flag && <img width={50} height={32} src={flag.png} alt={flag.alt} />}
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
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                  {panels.map((id) => (
                    <div key={id}>
                      <GrafanaPanel
                        countryIso={country.id}
                        from={dateRange.from}
                        to={dateRange.to}
                        panelId={id}
                      />
                    </div>
                  ))}
                </div>
              </Tabs.Panel>
            ))}
          </ScrollArea>
        </Tabs>
      </Box>
    </Overlay>
  );
}

export default CountryModal;
