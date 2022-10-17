import datetime
import random
import sys

import q100viz.session as session
import q100viz.devtools as devtools

class ModelValidation_Mode():
    def activate(self):
        ############################ Model Validation #########################

        batch_sim_start = datetime.datetime.now()

        # batch commands: shuffle buildings each time, GAMA branch = pre_main (not including change of agora dataset yet!)
        # 1. all false
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4)
        session.simulation.__init__()
        session.simulation.activate()

        # 2. connect in 2027
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045))
        session.simulation.__init__()
        session.simulation.activate()

        # 3. saniert true; rest false
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            refurbished=True)
        session.simulation.__init__()
        session.simulation.activate()

        # 4. Energiesparen true; rest false
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            save_energy=True)
        session.simulation.__init__()
        session.simulation.activate()

        # 5. Anschluss 2027; Saniert true; Energiesparen false
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045),
            refurbished=True)
        session.simulation.__init__()
        session.simulation.activate()

        # 6. Anschluss 2027; Saniert false; Energiesparen true
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045),
            save_energy=True)
        session.simulation.__init__()
        session.simulation.activate()

        # 7. Anschluss false; Saniert true; Energiesparen true
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            refurbished=True,
            save_energy=True)
        session.simulation.__init__()
        session.simulation.activate()

        # 8. Alles auf true
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.select_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045),
            save_energy=True,
            refurbished=True)
        session.simulation.__init__()
        session.simulation.activate()

        print("all simulations finished. total duration = ",
            datetime.datetime.now() - batch_sim_start)

        with open("qScope-log_%s.txt" % datetime.datetime.now(), "w") as f:
            f.write(session.log)
            f.close()
        sys.exit()
