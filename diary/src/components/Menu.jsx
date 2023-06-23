import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Link } from "react-router-dom";
import { Drawer, NavLink, Divider, Flex, ActionIcon } from "@mantine/core";
import { IconX } from "@tabler/icons-react";

import Logo from "./Logo";

function Menu({ opened, close, links }) {
  const location = useLocation();

  useEffect(() => {
    close();
  }, [location]);

  return (
    <Drawer
      opened={opened}
      onClose={close}
      withCloseButton={false}
      styles={{ inner: { zIndex: 300 }, overlay: { zIndex: 300 } }}
      size="xs"
    >
      <Flex justify="space-between" align={"center"}>
        <Logo onClick={close} />
        <ActionIcon onClick={close} size={36}>
          <IconX size="1rem" />
        </ActionIcon>
      </Flex>

      <Divider my="sm" />
      <div sx={{ marginTop: "24px" }}>
        {links.map(({ label, path, Icon }) => (
          <NavLink
            component={Link}
            to={path}
            key={label}
            disabled={!path}
            label={label}
            icon={<Icon size="1rem" stroke={1.5} />}
            p="lg"
            fontSize="xl"
            active={path === location.pathname}
          />
        ))}
      </div>
    </Drawer>
  );
}
export default Menu;
