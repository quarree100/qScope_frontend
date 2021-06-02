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

## recommended folder structure:

```
project qScope
└───cspy
│   └───CityScoPy LEGO Decoder
└───data
│       contains LINKS to GIS data from Seafile and api.json for SOFTWARE COMMUNICATION
└───GAMA
│   │   GAMA workspace folder
│   └───Project_RuesdorferKamp_Network
│   │   │   Project 1: Social Agents Communication Network
│   │	└───RuesdorferKamp_Network_Model-01.gaml
│   └───Project_RuesdorferKamp_Restoration
│    	└───Restoration_Model_01.gaml
└───q100_info
│       infoscreen script (javaScript)
└───q100_viz
│       projection script (P5)
└───settings
        initial setup data to initialize ALL SOFTWARE COMPONENTS centrally

```
where:
- cspy: https://github.com/dunland/cspy
- data: has to be linked from server
- GAMA: https://github.com/Lwinkeler/Q100-AB2-qScope
- q100_info: t.b.a
- q100_viz: https://github.com/dunland/q100_viz
- settings: t.b.a (currently from cspy/settings)
