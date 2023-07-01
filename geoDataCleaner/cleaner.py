import json

with open('geoData.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

new_data = {"features": []}

for feature in data['features']:
    new_feature = {
        "type": feature["type"],
        "properties": {
            "NAME": feature["properties"]["NAME"],
            "ISO_A2": feature["properties"]["ISO_A2"]
        },
        "geometry": feature["geometry"]
    }
    if new_feature["properties"]["ISO_A2"] == "-99":
        print(new_feature["properties"]["NAME"])
    new_data["features"].append(new_feature)

with open('output.json', 'w') as json_file:
    json.dump(new_data, json_file)
