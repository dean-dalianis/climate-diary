import {IconMoonStars, IconSun} from "@tabler/icons-react";
import {ActionIcon, useMantineColorScheme} from "@mantine/core";

function DarkModeSwitch() {
    const {colorScheme, toggleColorScheme} = useMantineColorScheme();

    return (
        <ActionIcon variant="default" onClick={() => toggleColorScheme()} size={30}>
            {colorScheme === "dark" ? (
                <IconSun size="1rem"/>
            ) : (
                <IconMoonStars size="1rem"/>
            )}
        </ActionIcon>
    );
}

export default DarkModeSwitch;
