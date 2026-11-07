import os
import sys
import xml.etree.ElementTree as ET
import re
import json
import zwift_wad

assets = (
    os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Zwift', 'assets'),
    os.path.expanduser('~/Library/Application Support/Zwift/assets'),
    os.path.expanduser('~/Documents/Zwift/assets')
)

source = next((d for d in assets if os.path.isdir(os.path.join(d, 'Worlds'))), None)
if source is None:
    sys.exit('Zwift assets not found')

world_to_course = {
    '1': (6, 'Watopia'),
    '2': (2, 'Richmond'),
    '3': (7, 'London'),
    '4': (8, 'New York'),
    '5': (9, 'Innsbruck'),
    '6': (10, 'Bologna'),
    '7': (11, 'Yorkshire'),
    '8': (12, 'Crit City'),
    '9': (13, 'Makuri Islands'),
    '10': (14, 'France'),
    '11': (15, 'Paris'),
    '12': (16, 'Gravel Mountain'),
    '13': (17, 'Scotland')
}

data = []

for world in world_to_course:
    wad = os.path.join(source, 'Worlds', 'world%s' % world, 'data_1.wad')
    files = dict(zwift_wad.entries(zwift_wad.read_wad(wad)))
    for file in files:
        if file.startswith('Worlds/world%s/routes/routes' % world):
            xml = files[file].decode('utf-8')
            tree = ET.fromstring(re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>")
            route = tree.find('route')
            if route.get('eventOnly') == '1':
                wname = world_to_course[world][1]
                name = route.get('name').strip()
                if not name.startswith(wname):
                    name = '%s - %s' % (wname, name)
                event = {
                    'name': name,
                    'route': int(route.get('nameHash')),
                    'distance': round(float(route.get('distanceInMeters')) + float(route.get('leadinDistanceInMeters')), 1),
                    'course': world_to_course[world][0],
                    'sport': 1 if route.get('sportType') == '2' else 0
                }
                data.append(event)

with open('../data/events.txt', 'w') as f:
    json.dump(sorted(data, key=lambda row: row['name']), f, indent=2)
