1. `process_osm.go` extracts building polygons from OSM PBF file in a hardcoded bounds.
2. `generate_many_procthor.py` takes each polygon and generates several versions of the house.
3. `procthor_cat.py` merges the generated houses into a single ProcTHOR JSON file so it can be loaded all at once into Unity.
