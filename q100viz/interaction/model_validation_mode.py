import datetime
import random
import sys

import q100viz.session as session
import q100viz.devtools as devtools
############################ Model Validation #########################

class ModelValidation_Mode():
    def activate(self):
        batch_sim_start = datetime.datetime.now()

        self.batch_experiment_1()

        print("all simulations finished. total duration = ",
            datetime.datetime.now() - batch_sim_start)

        with open("qScope-log_%s.txt" % datetime.datetime.now(), "w") as f:
            f.write(session.log)
            f.close()

        sys.exit()

    def batch_experiment_1(self):

        # batch commands: shuffle buildings each time, GAMA branch = pre_main (not including change of agora dataset yet!)
        # 1. all false
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4)
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 2. connect in 2027
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045))
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 3. saniert true; rest false
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            refurbished=True)
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 4. Energiesparen true; rest false
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            save_energy=True)
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 5. Anschluss 2027; Saniert true; Energiesparen false
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045),
            refurbished=True)
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 6. Anschluss 2027; Saniert false; Energiesparen true
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045),
            save_energy=True)
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 7. Anschluss false; Saniert true; Energiesparen true
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            refurbished=True,
            save_energy=True)
        session.simulation.__init__()
        session.active_mode = session.simulation


        # 8. Alles auf true
        session.buildings.load_data()  # re-init buildings
        session.environment['current_iteration_round'] = 0
        devtools.mark_random_buildings_for_simulation(
            session.buildings.df, 4,
            connection_to_heat_grid=random.randint(2020, 2045),
            save_energy=True,
            refurbished=True)
        session.simulation.__init__()
        session.active_mode = session.simulation


    def batch_experiment_2(self):
        # batch commands: select the same buildings each time, GAMA branch = agora_reduction
        pass

    def batch_experiment_3(self):
        # 8 simulations with changing num of connections
        pass
