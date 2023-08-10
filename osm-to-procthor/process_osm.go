package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"os"
	"strconv"
	"time"

	"github.com/qedus/osmpbf"
)

func decodeOsm(fname string, f func(v interface{})) {
	file, err := os.Open(fname)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	decoder := osmpbf.NewDecoder(file)
	decoder.SetBufferSize(osmpbf.MaxBlobSize)
	decoder.Start(32)
	for {
		if v, err := decoder.Decode(); err == io.EOF {
			break
		} else if err != nil {
			panic(err)
		} else {
			f(v)
		}
	}
}

func parseInt(s string) int {
	x, err := strconv.Atoi(s)
	if err != nil {
		panic(err)
	}
	return x
}

func lonLatToMercator(lon float64, lat float64) [2]int {
	n := math.Exp2(float64(18))
	x := (lon + 180) / 360 * n
	y := (1 - math.Log(math.Tan(lat*math.Pi/180)+(1/math.Cos(lat*math.Pi/180)))/math.Pi) / 2 * n
	return [2]int{int(x * 512), int(y * 512)}
}

func lonLatToCoordinate(bounds [4]float64, lon float64, lat float64) [2]int {
	originMercator := lonLatToMercator(bounds[0], bounds[3])
	myMercator := lonLatToMercator(lon, lat)
	return [2]int{
		myMercator[0] - originMercator[0],
		myMercator[1] - originMercator[1],
	}
}

type Way struct {
	NodeIDs []int64
}

type Node struct {
	X int
	Y int
}

func main() {
	// Download from https://download.geofabrik.de/north-america/us/washington.html
	osmPath := "washington-latest.osm.pbf"
	outPath := "buildings.json"

	bounds := [4]float64{
		//-122.334598, 47.675966,
		//-122.328979, 47.679285,

		-122.331870, 47.677559,
		-122.331543, 47.677776,
	}

	// First pass: decode ways.
	fmt.Println("decode ways")
	t0 := time.Now()
	count := 0
	ways := make(map[int64]Way)
	// Node ID to way ID that requested it.
	neededNodes := make(map[int64]int64)
	decodeOsm(osmPath, func(v interface{}) {
		switch v := v.(type) {
		case *osmpbf.Way:
			count++
			if count%1000000 == 0 {
				fmt.Printf("finished %dM ways (%v elapsed)\n", count/1000000, int(time.Now().Sub(t0).Seconds()))
			}
			if len(v.NodeIDs) < 2 {
				return
			}
			if v.Tags["building"] == "" {
				return
			}

			var way Way
			for _, nodeID := range v.NodeIDs {
				way.NodeIDs = append(way.NodeIDs, nodeID)
				neededNodes[nodeID] = v.ID
			}
			ways[v.ID] = way
		}
	})
	fmt.Printf("got %d ways\n", len(ways))

	// Second pass: decode nodes, record their mercator column/row.
	fmt.Println("decode nodes")
	t0 = time.Now()
	nodes := make(map[int64]Node)
	count = 0
	// Set of bad way IDs because at least one member node was outside the bounds.
	badWays := make(map[int64]bool)
	decodeOsm(osmPath, func(v interface{}) {
		switch v := v.(type) {
		case *osmpbf.Node:
			count++
			if count%10000000 == 0 {
				fmt.Printf("finished %dM nodes (%v elapsed)\n", count/1000000, int(time.Now().Sub(t0).Seconds()))
			}
			wayID := neededNodes[v.ID]
			if wayID == 0 || badWays[wayID] {
				return
			}
			if v.Lon < bounds[0] || v.Lon > bounds[2] || v.Lat < bounds[1] || v.Lat > bounds[3] {
				// Some way wanted this node but the node is out of bounds.
				// So mark the way bad.
				badWays[wayID] = true
				return
			}

			pos := lonLatToCoordinate(bounds, v.Lon, v.Lat)
			nodes[v.ID] = Node{
				X: pos[0],
				Y: pos[1],
			}
		}
	})
	fmt.Printf("got %d nodes\n", len(nodes))

	fmt.Println("preparing polygons")
	var polygons [][][2]int
	for wayID, way := range ways {
		if badWays[wayID] {
			continue
		}
		var vertices [][2]int
		missing := false
		for _, nodeID := range way.NodeIDs {
			node, ok := nodes[nodeID]
			if !ok {
				missing = true
				break
			}
			vertices = append(vertices, [2]int{node.X, node.Y})
		}
		if missing {
			continue
		}
		polygons = append(polygons, vertices)
	}

	fmt.Println("writing json")
	bytes, err := json.Marshal(polygons)
	if err != nil {
		panic(err)
	}
	if err := ioutil.WriteFile(outPath, bytes, 0644); err != nil {
		panic(err)
	}
}
