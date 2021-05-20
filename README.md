# q100_viz

Code für die Projektion und Bespielung des Monitors des CityScope-Setups in QUARREE100.

## q100viz_p5

*q100viz_p5* is a Python port of the *q100viz* Processing sketch. It relies heavily on the "p5" library (read the documentation [here](https://p5.readthedocs.io/)).

Before you can run the sketch, you need to install required packages:
```
pip install -r requirements.txt
```

Geodata sources are expected to be found in the `data` directory. Create it (if it does not exist) and make the basemap image and shapefiles available.

Change to the `q100viz_p5` directory and run the sketch:
```
python q100viz.py
```