import json
import math
import numpy as np
import os
import procthor.generation
import skimage.draw
import skimage.measure
import tqdm

in_fname = 'buildings.json'
out_dir = 'houses_v5_set2/'
factor = 7
scale = 1.5

with open(in_fname, 'r') as f:
    polygons = json.load(f)

house_generator = procthor.generation.HouseGenerator(
    split="train", seed=42, room_spec_sampler=procthor.generation.PROCTHOR10K_ROOM_SPEC_SAMPLER,
)

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

def get_bad_line_sum(vertices):
    edges = [
        (vertices[i], vertices[(i+1)%len(vertices)])
        for i in range(len(vertices))
    ]
    total = 0
    angle_threshold = math.pi / 60 # 3 degrees
    for edge in edges:
        dx = edge[1][0] - edge[0][0]
        dy = edge[1][1] - edge[0][1]
        angle = math.atan2(dx, dy)
        if abs(angle - 0) < angle_threshold or abs(angle - math.pi/2) < angle_threshold or abs(angle + math.pi/2) < angle_threshold or abs(angle - math.pi) < angle_threshold or abs(angle + math.pi) < angle_threshold:
            continue
        total += math.sqrt(dx*dx + dy*dy)
    return total

def render_polygon(vertices):
    # Render the rotated polygon onto a grid.
    # The resolution of the source data is roughly 0.3 m/pixel.
    # But we want to use a 1.5 m grid, so we downsample by a factor.
    bbox = [
        min([vertex[0] for vertex in vertices]),
        min([vertex[1] for vertex in vertices]),
        max([vertex[0] for vertex in vertices]),
        max([vertex[1] for vertex in vertices]),
    ]
    big_im = np.ones((bbox[3] - bbox[1] + 1, bbox[2] - bbox[0] + 1), dtype=np.int64)
    rr, cc = skimage.draw.polygon(
        np.array([vertex[1] - bbox[1] for vertex in vertices], dtype=np.int32),
        np.array([vertex[0] - bbox[0] for vertex in vertices], dtype=np.int32),
        shape=big_im.shape,
    )
    big_im[rr, cc] = 0

    im = skimage.measure.block_reduce(big_im, (factor, factor), np.max)

    # Autocrop image.
    while im[:, 0].min() == 1:
        im = im[:, 1:]
    while im[0, :].min() == 1:
        im = im[1:, :]
    while im[:, -1].min() == 1:
        im = im[:, :-1]
    while im[-1, :].min() == 1:
        im = im[:-1, :]

    return im

done_house_hits = {}
for fname in os.listdir(out_dir):
    house_idx = int(fname.split('.')[0].split('_')[0])
    done_house_hits[house_idx] = done_house_hits.get(house_idx, 0) + 1

for house_idx, vertices in tqdm.tqdm(list(enumerate(polygons))):
    if done_house_hits.get(house_idx, 0) >= 3:
        continue

    # Get center of bbox around polygon and use it as its rotation origin.
    bbox = [
        min([vertex[0] for vertex in vertices]),
        min([vertex[1] for vertex in vertices]),
        max([vertex[0] for vertex in vertices]),
        max([vertex[1] for vertex in vertices]),
    ]
    rotation_origin = [
        (bbox[0]+bbox[2])//2,
        (bbox[1]+bbox[3])//2,
    ]
    vertices = [
        (vertex[0] - rotation_origin[0], vertex[1] - rotation_origin[1])
        for vertex in vertices
    ]
    print('initial', render_polygon(vertices))

    # Try 360 rotations of the vertices.
    # Pick the one with the shortest total line segment that are not close to 0, 90, 180, or 270 degrees.
    lowest_bad_line_sum = None
    best_vertices = []
    best_degrees = None
    for degrees in range(360):
        radians = degrees * math.pi / 180
        cur_vertices = [
            rotate(vertex, radians)
            for vertex in vertices
        ]
        bad_line_sum = get_bad_line_sum(cur_vertices)
        if lowest_bad_line_sum is None or bad_line_sum < lowest_bad_line_sum:
            lowest_bad_line_sum = bad_line_sum
            best_vertices = cur_vertices
            best_degrees = degrees

    print('reduce bad line sum from', get_bad_line_sum(vertices), 'to', get_bad_line_sum(best_vertices))

    origin = (rotation_origin[0]//factor, rotation_origin[1]//factor)
    im = render_polygon(best_vertices)
    print(im)

    if skimage.measure.label(1-im, connectivity=1).max() > 1:
        print('bad house')
        continue

    for rand_idx in range(3):
        for _ in range(3):
            try:
                # Generate fully random house to get a randomized room_spec.
                random_house, _ = house_generator.sample()
                room_spec = random_house.room_spec

                # Create partial house with the interior boundary and room spec.
                house_structure = house_generator.generation_functions.sample_house_structure(
                    interior_boundary=im,
                    room_ids=room_spec.room_type_map.keys(),
                    room_spec=room_spec,
                    interior_boundary_scale=scale,
                )
                partial_house = procthor.generation.PartialHouse.from_structure_and_room_spec(
                    house_structure=house_structure,
                    room_spec=room_spec,
                )
                partial_house.next_sampling_stage = procthor.generation.NextSamplingStage.DOORS

                house, _ = house_generator.sample(partial_house=partial_house)

                house.to_json(os.path.join(out_dir, '{}_{}_{}_{}_{}.json'.format(house_idx, origin[0], origin[1], best_degrees, rand_idx)))
                print('success')
                break
            except Exception as e:
                print(e)
