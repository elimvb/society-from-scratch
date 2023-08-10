import json
import math
import numpy as np
import os
import skimage.draw
import skimage.io

# This needs to match scale from generate_many_procthor.py.
scale = 1.5
unrotate = False

json_and_offset = []
for fname in os.listdir('procthor/houses/'):
    if not fname.endswith('_0.json'):
        continue
    parts = fname.split('.')[0].split('_')
    offset = (int(parts[1]), int(parts[2]))
    degrees = int(parts[3])
    json_and_offset.append(('procthor/houses/' + fname, (offset[1]*scale, offset[0]*scale), -degrees*math.pi/180))

final = {
    'doors': [],
    'objects': [],
    'rooms': [],
    'walls': [],
    'windows': [],
}
next_room_id = 1
used_obj_ids = set()
used_door_ids = set()
used_window_ids = set()

def handle_obj(obj, center_offset, radians, center):
    while obj['id'] in used_obj_ids:
        obj['id'] += '0'
    used_obj_ids.add(obj['id'])

    update_point_dict(obj['position'], center_offset, radians, center)
    if unrotate:
        obj['rotation']['y'] += int(radians * 180 / math.pi)

    for child in obj.get('children', []):
        handle_obj(child, center_offset, radians, center)

def rotate(point, angle):
    """
    Rotate a point counterclockwise by a given angle.

    The angle should be given in radians.
    """
    px, py = point
    return (
        int(math.cos(angle) * px - math.sin(angle) * py),
        int(math.sin(angle) * px + math.cos(angle) * py),
    )

def update_point_dict(d, center_offset, radians, center):
    x = d['x']
    z = d['z']
    x = x - center[0]
    z = z - center[1]
    if unrotate:
        z, x = rotate((z, x), radians)
    x += center_offset[0]
    z += center_offset[1]
    d['x'] = x
    d['z'] = z

mask_im = np.zeros((600, 600, 3), dtype=np.uint8)
colors = [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [255, 0, 255],
    [0, 255, 255],
    [255, 255, 255],
    [128, 128, 128],
    [60, 179, 113],
    [238, 130, 238],
    [106, 90, 205],
    [255, 165, 0],
]

for json_idx, (json_fname, center_offset, radians) in enumerate(json_and_offset):
    color = colors[json_idx % len(colors)]

    with open(json_fname, 'r') as f:
        data = json.load(f)

    final['metadata'] = data['metadata']
    final['proceduralParameters'] = data['proceduralParameters']

    # Compute offset based on provided center_offset, and the actual center of this house.
    xs = [coord['x'] for room in data['rooms'] for coord in room['floorPolygon']]
    zs = [coord['z'] for room in data['rooms'] for coord in room['floorPolygon']]
    bbox = (
        min(xs),
        min(zs),
        max(xs),
        max(zs),
    )
    center = (
        (bbox[0]+bbox[2])/2,
        (bbox[1]+bbox[3])/2,
    )

    room_id_map = {}
    for room in data['rooms']:
        new_room_id = 'room|{}'.format(next_room_id)
        next_room_id += 1
        room_id_map[room['id']] = new_room_id
        room['id'] = new_room_id

        for coord in room['floorPolygon']:
            update_point_dict(coord, center_offset, radians, center)

        final['rooms'].append(room)

        xs = np.array([p['x'] for p in room['floorPolygon']], dtype=np.int32)
        ys = np.array([p['z'] for p in room['floorPolygon']], dtype=np.int32)
        rr, cc = skimage.draw.polygon(xs, ys, shape=mask_im.shape)
        mask_im[rr, cc, :] = color

    wall_id_map = {}
    for wall in data['walls']:
        parts = wall['id'].split('|')
        new_wall_id = '{}|{}|{}|{}|{}|{}'.format(
            parts[0], parts[1],
            float(parts[2])+center_offset[0],
            float(parts[3])+center_offset[1],
            float(parts[4])+center_offset[0],
            float(parts[5])+center_offset[1],
        )
        wall_id_map[wall['id']] = new_wall_id
        wall['id'] = new_wall_id

        wall['roomId'] = room_id_map[wall['roomId']]

        for coord in wall['polygon']:
            update_point_dict(coord, center_offset, radians, center)

        final['walls'].append(wall)

    for obj in data['objects']:
        handle_obj(obj, center_offset, radians, center)
        final['objects'].append(obj)

    for door in data['doors']:
        while door['id'] in used_door_ids:
            door['id'] += '0'
        used_door_ids.add(door['id'])

        door['room0'] = room_id_map[door['room0']]
        door['room1'] = room_id_map[door['room1']]
        door['wall0'] = wall_id_map[door['wall0']]
        door['wall1'] = wall_id_map[door['wall1']]
        final['doors'].append(door)

    for window in data['windows']:
        while window['id'] in used_window_ids:
            window['id'] += '0'
        used_window_ids.add(window['id'])

        window['room0'] = room_id_map[window['room0']]
        window['room1'] = room_id_map[window['room1']]
        window['wall0'] = wall_id_map[window['wall0']]
        window['wall1'] = wall_id_map[window['wall1']]
        final['windows'].append(window)

with open('final.json', 'w') as f:
    json.dump(final, f)

skimage.io.imsave('mask.png', mask_im)
