# example script to start the gama-headless.sh bash file via python.
# @dunland, March 2022

import subprocess
import pandas as pd
import os
from config import config

class Simulation:

    def __init__(self,
        headless_folder = config['GAMA_HEADLESS_FOLDER'],
        model_file = config['GAMA_MODEL_FILE'],
        output_folder= config['GAMA_OUTPUT_FOLDER'],
        final_step= 200,
        until=None,
        experiment_name="agent_decision_making"):

        """
        - experiment_name must be identical to GAMA experiment.
        - gama-headless.sh must stay in folder relative to gama executable --> use absolute path
        """

        self.headless_folder = headless_folder
        self.script = headless_folder + 'gama-headless.sh'
        self.model_file = model_file
        self.output_folder = output_folder

        self.xml = None

        # simulation data:
        self.final_step = final_step
        self.until = until
        self.experiment_name = experiment_name

        self.cwd = os.getcwd()  # hold current working directory to return to later

    def make_xml(self, parameters, outputs, finalStep=None, until=None, experiment_name=None):
        # header
        xml_temp = ['<Experiment_plan>']
        if until is not None:
            xml_temp.append('  <Simulation id="1" sourcePath="{0}" finalStep="{1}" until="{2}" experiment="{3}" >'.format(str(self.model_file), str(finalStep), str(until), str(experiment_name)))
        else:
            xml_temp.append('  <Simulation id="1" sourcePath="{0}" finalStep="{1}" experiment="{2}" >'.format(str(self.model_file), str(finalStep), str(experiment_name)))

        # parameters
        xml_temp.append('  <Parameters>')
        for index, row in parameters.iterrows():
            xml_temp.append('    <Parameter name="{0}" type="{1}" value="{2}" />'.format(row['name'], row['type'], row['value']))
        xml_temp.append('  </Parameters>')

        # outputs
        xml_temp.append('  <Outputs>')
        for index, row in outputs.iterrows():
            xml_temp.append('    <Output id="{0}" name="{1}" framerate="{2}" />'.format(row['id'], row['name'], row['framerate']))
        xml_temp.append('  </Outputs>')
        xml_temp.append('</Simulation>')
        xml_temp.append('</Experiment_plan>')

        xml = '\n'.join(xml_temp)

        # export xml
        if os.path.isdir(self.output_folder) is False:
            os.mkdir(self.output_folder)
        os.chdir(self.headless_folder)  # change working directory temporarily

        print(xml)
        f = open(self.headless_folder + 'simulation_parameters.xml', 'w')
        f.write(xml)
        f.close()

    def run_script(self):
        # run script
        xml_path = self.headless_folder + 'simulation_parameters.xml'
        command = self.script + " " + xml_path + " " + self.output_folder
        subprocess.call(command, shell=True)

        os.chdir(self.cwd)  # return to previous cwd