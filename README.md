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

### Flags

- `--main_window`: runs canvas in current window
- `--verbose`: start in verbose mode
- `--start_at [mode]`: which mode to start in? can be any of buildings_interaction, simulation, individual_data_view, total_data_view
- `--simulate_until [YEAR]`: define max year of simulation
- `--select_random [N]`: select random n buildings...
- `--connect [YEAR]`: ... and connect selected buildings to heat grid
- `--refurbish [YEAR]`: ... set date for refurbishment of selected buildings
- `--save_energy`: ... require selected buildings to enable energy saving
- `--research_model`: use research agent-based-model (defined in [config.py](q100viz/settings/config.py) instead of the standard designated workshop-abm)

### Interactions

- **P** key: toggle polygons
- **M** key: toggle basemap
- **G** key: toggle grid
- **C** key: toggle calibration mode
- **V** key: toggle verbose mode --> will print more information and export the canvas.png continuously

- In calibration mode:
  - **TAB** key: select active corner
  - **UP/DOWN/LEFT/RIGHT** keys: move active corner
  - **SPACE**: toggle magnitude
  - **S** key: save configuration

## Recommended folder structure

```
project qScope
└───cspy
│   └───modified MIT CityScoPy Token Tag Decoder
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
- cspy: https://github.com/quarree100/cspy
- data: has to be linked from Seafile server
- GAMA: https://github.com/quarree100/q100_abm
- qScope_infoscreen: https://github.com/quarree100/qScope_infoscreen
- qScope_frontend: https://github.com/quarree100/qScope_frontend


## further requirements:
- GAMA (1.8.2) has to be installed and the path to its headless folder has to be provided in config.py
