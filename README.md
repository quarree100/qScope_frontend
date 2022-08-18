# qScope_frontend

Code für die Projektion und Interaktion via _Tangible User Interface_ des Q-Scope-Setups (basierend auf dem MIT-CityScope-Projekt) in QUARREE100.

## q100viz
*q100viz* is based on [pygame](https://www.pygame.org/).

Find some documentation at q-scope.readthedocs.io/

Before you can run the sketch, you need to install required packages:
```
pip install -r requirements.txt
```

Geodata sources are expected to be found in the `data` directory. Create it (if it does not exist) and make the basemap image and shapefiles available. Check the file paths in `config.py`.

Run the sketch:
```
python run_q100viz.py
```

### Interactions

- **P** key: toggle polygons
- **M** key: toggle basemap
- **G** key: toggle grid
- **C** key: toggle calibration mode
- **V** key: toggle verbose mode

- In calibration mode:
  - **TAB** key: select active corner
  - **UP/DOWN/LEFT/RIGHT** keys: move active corner
  - **SPACE**: toggle magnitude
  - **S** key: save configuration

## Recommended folder structure

```
project qScope
└───cspy
│   └───MIT CityScoPy Token Tag Decoder (modified by dunland)
└───data
|   └───outputs
|      └───output_[timestamp]
|         (simulation-specific output)
|         └───buildings_clusters_[timestamp].csv
|         (exportierte Gebäudeliste von Frontend)
|         └───simulation_parameters_[timestamp].xml
|         (xml-Datei mit allen Simulationsparametern zum Starten des headless modes)
|         └───connections
|         |       Export der Anschlussquoten
|         └───emissions
|         |      gebäudespezifische und aggregierte Quartiersemissionen
|         └───snapshot
|               von GAMA produzierte Grafiken
└───q100_abm
│   │   GAMA workspace folder
│   └───q100
│       │   Trend Model
│    	└───models
|       │    └───qscope_ABM.gaml
|       └───__data__ symlink zu data-Ordner (unten))
└───qScope_infoscreen
│       infoscreen (NodeJS/ JavaScript)
└───qScope_frontend
        projection (Python)

```

where:
- cspy: https://github.com/dunland/cspy
- data: has to be linked from Seafile server
- GAMA: https://github.com/quarree100/q100_abm
- qScope_infoscreen: https://github.com/quarree100/qScope_infoscreen
- qScope_frontend: https://github.com/quarree100/qScope_frontend


## further requirements:
- GAMA has to be installed and the path to its headless folder has to be provided in config.py
