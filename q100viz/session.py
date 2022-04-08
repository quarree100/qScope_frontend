'''This module keeps variables shared among other modules.'''

from q100viz.interaction.calibration_mode import CalibrationMode
# from q100viz.interaction.edit_mode import EditMode
from q100viz.interaction.input_mode import InputMode
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.questionnaire_mode import Questionnaire_Mode


# graphics
viewport = None
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
verbose = True
slider_handles = ['year', 'funding', 'CO2-prize', 'connection_speed',
                    'CO2-emissions', 'electricity_supplier', 'connection_to_heat_grid', 'refurbished', 'answer']
environment = dict.fromkeys(slider_handles, 0)
environment['mode'] = 'input'

environment['questions'] = [  # TODO: externalize this to yet another csv

        "Die globale Erderwärmung wird durch von Menschen produzierte Emissionen verstärkt.",
        "Der Schutz der Umwelt ist ein Mittel zur Stärkung des Wirtschaftswachstums in Deutschland.",
        "Ich glaube, dass wir jedes Mal, wenn wir Kohle, Öl oder Gas verwenden, zum Klimawandel beitragen.",
        "Ich würde meinen Energieverbrauch reduzieren, wenn mein Haushalt mehr Energie verbraucht als ähnliche Haushalte.",
        "Wenn ein erneuerbarer Energietarif bei einem anderen Energieversorger verfügbar wäre, würde ich meinen Anbieter wechseln."
]
environment['question'] = environment['questions'][0]

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

handlers = {
    'calibrate': CalibrationMode(),
    # 'edit': EditMode(),
    'input': InputMode(),
    'simulation': SimulationMode(),
    'questionnaire': Questionnaire_Mode()
}
active_handler = handlers['questionnaire']
flag_export_canvas = False

# global functions:
def print_verbose(message):
    if verbose:
        print(message)