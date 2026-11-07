import os
import sys
import xml.etree.ElementTree as ET
import re
import json
from urllib3 import PoolManager
import zwift_wad

assets = (
    os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Zwift', 'assets'),
    os.path.expanduser('~/Library/Application Support/Zwift/assets'),
    os.path.expanduser('~/Documents/Zwift/assets')
)

source = next((d for d in assets if os.path.isdir(os.path.join(d, 'Worlds'))), None)
if source is None:
    sys.exit('Zwift assets not found')

world_names = {
    '1': 'Watopia',
    '2': 'Richmond',
    '3': 'London',
    '4': 'New York',
    '5': 'Innsbruck',
    '6': 'Bologna',
    '7': 'Yorkshire',
    '8': 'Crit City',
    '9': 'Makuri Islands',
    '10': 'France',
    '11': 'Paris',
    '12': 'Gravel Mountain',
    '13': 'Scotland'
}

data = {}

for world in world_names:
    wad = os.path.join(source, 'Worlds', 'world%s' % world, 'data_1.wad')
    files = dict(zwift_wad.entries(zwift_wad.read_wad(wad)))
    for file in files:
        if file.startswith('Worlds/world%s/routes/routes' % world):
            xml = files[file].decode('utf-8')
            tree = ET.fromstring(re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>")
            route = tree.find('route')
            nameHash = int.from_bytes(int(route.get('nameHash')).to_bytes(4, 'little'), 'little', signed=True)
            checkpoints = list(tree.find('highrescheckpoint').iter('entry'))
            data[nameHash] = {
                'name': '%s - %s' % (world_names[world], route.get('name').strip()),
                'road': int(checkpoints[0].get('road')),
                'time': int(float(checkpoints[0].get('time')) * 1000000 + 5000)
            }

base_url = 'https://loveturtle.zwift.com/1.0.2/'
manifest = PoolManager().request('GET', base_url + 'watopian/watopian.manifest.json').json()
for collection in manifest['collections']:
    for ride in collection['rides']:
        route_hash = int.from_bytes(int(ride['route_hash']).to_bytes(4, 'little'), 'little', signed=True)
        xml = PoolManager().request('GET', base_url + ride['route']['key']).data.decode('utf-8')
        tree = ET.fromstring('<root>%s</root>' % xml)
        checkpoints = list(tree.find('highrescheckpoint').iter('entry'))
        data[route_hash] = {
            'name': 'Video - ' + ride['pretty_name'],
            'road': ride['road_id'],
            'time': int(float(checkpoints[0].get('time')) * 1000000 + 5000)
        }

with open('../data/start_lines.txt', 'w') as f:
    json.dump({k: v for k, v in sorted(data.items(), key=lambda d: d[1]['name'])}, f, indent=2)
