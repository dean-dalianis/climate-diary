import {Card, List, Paper, Text, Title, useMantineTheme} from "@mantine/core";

export default function About() {

    const {colorScheme} = useMantineTheme();
    const diagram = colorScheme === 'light' ? 'diagram_light.svg' : 'diagram_dark.svg';
    return (
        <Paper style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            padding: "2em",
            gap: "2em",
            paddingTop: '6em',
            paddingBottom: '5em',
            paddingLeft: '10em',
            paddingRight: '10em'
        }}>
            <div style={{display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap'}}>
                <Card padding="md" shadow="xs" style={{width: '45%', padding: '2em', margin: '2em'}}>
                    <Title order={1} style={{paddingBottom: '0.3em'}}>About Climate Diary</Title>
                    <Text size="lg">
                        Welcome to the Climate Diary! A one-of-a-kind project that enables users to fetch, access, and
                        visualize climate data for countries worldwide. We provide an easy-to-use, intuitive platform
                        that
                        not only presents data but also tells a story. Our project comprises various components, each
                        serving a unique function in the data extraction, processing, and visualization process.
                    </Text>
                    <br/>
                    <Text size="lg">
                        In the realm of climate data, we believe in the power of accessibility and understandability.
                        Climate Diary is designed to bridge the gap between complex climate data and people from all
                        walks
                        of life. Our platform is more than just a tool; it's a window into the world's climate patterns
                        and
                        a catalyst for insightful discussions. With each piece of data, we strive to foster a broader
                        understanding of our planet's intricate climate systems. We've crafted a user experience that
                        makes
                        complex climate data digestible and actionable, serving as an invaluable resource for climate
                        enthusiasts, researchers, educators, and the naturally curious. As we continue to evolve and
                        improve, we invite you to join us on this journey of discovery and education.
                    </Text>
                </Card>

                <Card padding="md" shadow="xs" style={{width: '45%', padding: '2em', margin: '2em'}}>
                    <Title order={1} style={{paddingBottom: '0.3em'}}>Our Data</Title>
                    <Text size="lg">
                        We currently use the Global Summary of the Year (GSOY) data provided by the National Oceanic and
                        Atmospheric Administration (NOAA). The data incorporates a range of climate-related
                        measurements,
                        including temperature extremes, precipitation, snowfall, and days with thunder or fog, among
                        others.

                        While our current model only supports a limited set of measurements, we have designed our system
                        with future expansion in mind. We plan to add more measurements and information about:
                        <br/>
                        <br/>
                        <List size="lg" withPadding>
                            <List.Item>air quality</List.Item>
                            <List.Item>weather stations</List.Item>
                            <List.Item>local weather patterns</List.Item>
                            <List.Item>carbon emissions</List.Item>
                            <List.Item>socioeconomic data</List.Item>
                        </List>
                    </Text>
                </Card>

                <Card padding="md" shadow="xs" style={{padding: '2em', margin: '2em'}}>
                    <div style={{
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: 'start',
                        justifyContent: 'space-between'
                    }}>
                        <div style={{width: '50%', paddingRight: '2em'}}>
                            <Title order={1} style={{paddingBottom: '0.3em'}}>Architecture</Title>
                            <Text size="lg">
                                The <b>Climate Diary</b> project is built on a strong foundation of powerful open-source
                                technologies. This has allowed us to create an interactive and highly flexible platform
                                that delivers an unparalleled user experience.
                            </Text>
                            <br/>
                            <Text size="lg">
                                We utilize <b>Leaflet</b>, a leading open-source JavaScript library for mobile-friendly
                                interactive maps. Leaflet provides us with a lightweight, yet incredibly powerful
                                mapping service, allowing our users to zoom, pan, and interact with our climate data
                                geographically. Its plug-and-play approach means we can customize map features to suit
                                our needs, making the user experience seamless and intuitive.
                            </Text>
                            <br/>
                            <Text size="lg">
                                Our platform also integrates <b>Grafana</b>, a robust open-source software for
                                visualizing time series data. Grafana excels in its ability to present complex datasets
                                in a manner that's easy to understand, regardless of your background. It provides a
                                myriad of options for data visualization, such as bar charts, line graphs, heat maps,
                                and many more, giving our users the flexibility to view data in a format that best suits
                                their needs.
                            </Text>
                            <br/>
                            <Text size="lg">
                                To ensure our data is up-to-date and dynamic, we've integrated <b>Flux</b>, a data
                                scripting and query language from InfluxDB. This allows us to manipulate the data
                                on-the-fly, creating data trends and correlations that help our users gain deeper
                                insights into the climate data.
                            </Text>
                            <br/>
                            <Text size="lg">
                                Our goal is to provide an engaging platform for users to interact with and interpret
                                climate data in a user-friendly, visually appealing manner. By leveraging these powerful
                                tools, we've been able to create a platform that not only provides data but tells a
                                story, empowering our users to make informed discussions about our planet's climate.
                            </Text>
                        </div>
                        <div style={{
                            width: '45%',
                            padding: '1em',
                            display: 'flex',
                            justifyContent: 'center'
                        }}>
                            <img src={diagram} alt='Architecture' style={{width: '95%'}}/>
                        </div>
                    </div>
                </Card>

                <Card padding="md" shadow="xs" style={{width: '30%', padding: '2em', margin: '2em'}}>
                    <Title order={1} style={{paddingBottom: '0.3em'}}>Get Involved</Title>
                    <Text size="lg">

                        Whether you're a climate enthusiast, a student, a researcher, or simply curious, Climate Diary
                        offers a unique platform to explore and analyze climate data. We encourage you to immerse
                        yourself in the data, identify patterns, and perhaps even uncover something new.
                    </Text>
                    <br/>
                    <Text size="lg">
                        At the moment, while Climate Diary is designed with a spirit of openness and collaboration, we
                        are still in the process of setting up the necessary structures to facilitate and manage
                        open-source contributions effectively. This includes preparing our documentation, establishing
                        guidelines, and putting in place a robust system for handling pull requests and issues. As we
                        work towards making Climate Diary a vibrant open-source project, we still greatly value
                        your interest, engagement, and feedback. Please feel free to reach out with your thoughts and
                        suggestions, as these are invaluable in guiding our development efforts.
                    </Text>
                    <br/>
                    <Text size="lg">
                        We're excited about the journey ahead as we shape Climate Diary into a rich resource for climate
                        data, and we look forward to sharing this journey with you once we're ready to open up for
                        contributions.
                    </Text>
                    <Text size="lg">
                        Thank you for your understanding and patience. Stay tuned for updates!
                    </Text>
                </Card>


                <Card padding="md" shadow="xs" style={{width: '30%', padding: '2em', margin: '2em'}}>
                    <Title order={1} style={{paddingBottom: '0.3em'}}>Project Links</Title>
                    <Text size="lg">
                        <a href='https://github.com/dean-dalianis/dataVisualisation'>GitHub Repository</a><br/>
                        <a href='https://www.ncei.noaa.gov/data/gsoy/'>NOAA GSOY Data</a><br/>
                        <a href='http://209.38.220.161:3000/d/c351f1fe-59e9-4758-b061-93603cbedc6d/noaa-gsom-dashboard?orgId=1/'>Grafana</a><br/>
                        <a href='http://209.38.220.161:8000/'>Swagger UI</a>
                    </Text>
                </Card>

                <Card padding="md" shadow="xs" style={{width: '30%', padding: '2em', margin: '2em'}}>
                    <Title order={1} style={{paddingBottom: '0.3em'}}>Who are we?</Title>
                    <Text size="lg">
                        <a href='https://www.linkedin.com/in/kdalianis/'>Konstantinos Dalianis</a><br/>
                        <a href='https://www.linkedin.com/in/konstantinos-malonas-28793910a/'>Konstantinos
                            Malonas</a><br/>
                        <a href='https://www.linkedin.com/in/mdarm/'>Michael Darmanis</a><br/>
                    </Text>
                </Card>

            </div>
        </Paper>
    );
}
