# q100_viz
Processing-Code für die Projektion und Bespielung des Monitors des CityScope-Setups in QUARREE100.

## Notes
~~Die Processing-Sketche in [q100viz](q100viz/) lassen sich nur mit Processing 2 ausführen! Die verwendete Keystone-Library ist leider für Processing 3 nicht verfügbar..~~

Die verwendeten libraries befinden sich in `libraries.zip` und müssen in den Processing-Sketch-Folder eingefügt werden, z.B. `/home/user/sketchbook/libraries`

q100viz und statsViz müssen derzeit noch in bestimmer Reihenfolge ausgeführt werden, die mir gerade unklar ist..

## folder structure

```
project
└───lib
│	libraries needed for the execution of the processing sketches
└───q100viz
│       processing 2 sketch for the projection
└───statsViz
│       processing sketch for the monitor stats
└───libraries.zip
	contains all relevant processing libraries
```

## q100viz_p5

*q100viz_p5* is a Python port of the *q100viz* Processing sketch. 

Before you can run the sketch, you need to install required packages:
```
pip install -r requirements.txt
```

Geodata sources are expected to be found in the `data` directory. Create it (if it does not exist) and make the basemap image and shapefiles available.

Change to the `q100vix_p5` directory and run the sketch:
```
python q100viz.py
```