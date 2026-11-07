import os
import sys
import xml.etree.ElementTree as ET
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

data = []

wad = os.path.join(source, 'Worlds', 'roads.wad')
files = dict(zwift_wad.entries(zwift_wad.read_wad(wad)))
for file in files:
    if file.startswith('Worlds/portal/road_'):
        tree = ET.fromstring(files[file].decode('utf-8'))
        metadata = tree.find('.//metadata')
        name = metadata.find('m_PortalRoadUserFacingName').text
        length = round(float(metadata.find('m_PortalRoadCourseLength').text) / 100000, 1)
        if length.is_integer():
            length = int(length)
        ascent = int(float(metadata.find('m_PortalRoadCourseAscentF').text) / 100)
        climb = {
            'name': '%s (%s km / %s m)' % (name, length, ascent),
            'road': metadata.find('m_PortalRoadHash').text
        }
        data.append(climb)

with open('../data/climbs.txt', 'w') as f:
    json.dump(sorted(data, key=lambda row: row['name']), f, indent=2)
