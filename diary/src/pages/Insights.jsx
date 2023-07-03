import {Paper, Center, Title} from "@mantine/core";

function Insights() {
    return (
        <Paper sx={{width: "100vw", height: "100vh"}}>
            <Center w={"100%"} h={"100%"}>
                <iframe width="90%" height="90%" src="http://209.38.220.161:3000/d/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard"/>
            </Center>
        </Paper>
    );
}

export default Insights;
