# example script to start the gama-headless.sh bash file via python.
# @dunland, March 2022

import subprocess
import threading
import os
from q100viz.settings.config import config
import q100viz.session as session

class Simulation:

    def __init__(self,
        headless_folder = config['GAMA_HEADLESS_FOLDER'],
        model_file = config['GAMA_MODEL_FILE'],
        output_folder= config['GAMA_OUTPUT_FOLDER'],
        finalStep= 200,
        until=None,
        experiment_name="agent_decision_making"):

        """
        - experiment_name must be identical to GAMA experiment.
        - gama-headless.sh must stay in folder relative to gama executable --> use absolute path
        """
        self.cwd = os.getcwd()  # hold current working directory to return to later

        self.headless_folder = headless_folder
        self.script = self.headless_folder + 'gama-headless.sh'
        self.model_file = os.path.normpath(os.path.join(self.cwd, model_file))
        self.output_folder = os.path.normpath(os.path.join(self.cwd, output_folder))

        print("headless_folder =", self.headless_folder, "script = ", self.script, "model_file = ", self.model_file, "output_folder = ", self.output_folder)

        self.xml = None

        # simulation data:
        self.finalStep = finalStep
        self.until = until
        self.experiment_name = experiment_name


    def make_xml(self, parameters, outputs, finalStep=None, until=None, experiment_name=None, seed=1.0):
        # header
        xml_temp = ['<Experiment_plan>']
        # if until is not None:
            # xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}" until="{3}" experiment="{4}" seed="{5}">'.format(str(experiment_name), str(self.model_file), str(finalStep), str(until), str(experiment_name), str(seed)))

        xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}"'.format(str(experiment_name), str(self.model_file), str(finalStep)))
        if seed is not None: xml_temp.append('seed="{0}"'.format(str(seed)))
        if until is not None: xml_temp.append('until="{0}"'.format(str(until)))
        xml_temp.append('>')

        # else:
        #     xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}" >'.format(str(experiment_name), str(self.model_file), str(finalStep)))

        # parameters
        xml_temp.append('  <Parameters>')
        for index, row in parameters.iterrows():
            xml_temp.append('    <Parameter name="{0}" type="{1}" value="{2}" var="{3}"/>'.format(row['name'], row['type'], row['value'], row['var']))
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
            os.makedirs(self.output_folder)
        os.chdir(self.headless_folder)  # change working directory temporarily

        print(xml)
        f = open(self.headless_folder + '/simulation_parameters.xml', 'w')
        f.write(xml)
        f.close()

    def run_script(self, xml_path_):
        # run script
        if not xml_path_:
            xml_path = self.headless_folder + '/simulation_parameters.xml'
        else: xml_path = xml_path_
        command = self.script + " " + xml_path + " " + self.output_folder
        subprocess.call(command, shell=True)
        # self.open_and_call(command, session.handlers['data_view'].activate())

        os.chdir(self.cwd)  # return to previous cwd

        # TODO: wait until GAMA delivers outputs
        session.handlers['data_view'].activate()

    def open_and_call(self, popen_args, on_exit):

        def run_in_thread(on_exit, popen_args):
            proc = subprocess.Popen(popen_args, shell=True)
            proc.wait()
            on_exit()
            return

        thread = threading.Thread(target=run_in_thread, args=(on_exit, popen_args))
        thread.start()
        return thread