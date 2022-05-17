# example script to start the gama-headless.sh bash file via python.
# @dunland, March 2022

import subprocess
import pandas as pd
import os

headless_folder = '/home/dunland/opt/GAMA/headless/'
script = headless_folder + 'gama-headless.sh'
simulation_file = '/home/dunland/github/qScope/q100_abm/q100/models/qscope_ABM.gaml'
output_folder = "/home/dunland/github/qScope/q100_abm/q100/outputHeadless"


# simulation data:
final_step = 200
until = None
experiment_name = "agent_decision_making"  # must be identical to GAMA experiment

def compose_xml(parameters, outputs, simulation_file, finalStep=None, until=None, experiment_name=None):
    # header
    xml = ['<Experiment_plan>']
    if until is not None:
        xml.append('  <Simulation id="1" sourcePath="{0}" finalStep="{1}" until="{2}" experiment="{3}" >'.format(str(simulation_file), str(finalStep), str(until), str(experiment_name)))
    else:
        xml.append('  <Simulation id="1" sourcePath="{0}" finalStep="{1}" experiment="{2}" >'.format(str(simulation_file), str(finalStep), str(experiment_name)))

    # parameters
    xml.append('  <Parameters>')
    for index, row in parameters.iterrows():
        xml.append('    <Parameter name="{0}" type="{1}" value="{2}" />'.format(row['name'], row['type'], row['value']))
    xml.append('  </Parameters>')

    # outputs
    xml.append('  <Outputs>')
    for index, row in outputs.iterrows():
        xml.append('    <Output id="{0}" name="{1}" framerate="{2}" />'.format(row['id'], row['name'], row['framerate']))
    xml.append('  </Outputs>')
    xml.append('</Simulation>')
    xml.append('</Experiment_plan>')

    return '\n'.join(xml)

def main():
    # provide data:
    outputs = pd.DataFrame(columns=['id', 'name', 'framerate'])
    outputs.loc[len(outputs)] = ['0', 'neighborhood', '1']
    outputs.loc[len(outputs)] = ['1', 'households_income_bar', '5']

    params = pd.DataFrame(columns=['name', 'type', 'value'])
    params.loc[len(params)] = ['1', 'int', '500']
    params.loc[len(params)] = ['eeh', 'float', '0.3']
    params.loc[len(params)] = ['investment', 'int', '15123']

    # compose xml
    xml = compose_xml(params, outputs, simulation_file, finalStep=final_step, experiment_name=experiment_name)

    # export xml
    if os.path.isdir(output_folder) is False:
        os.mkdir(output_folder)
    os.chdir(headless_folder)

    print(xml)
    f = open('simulation_parameters.xml', 'w')
    f.write(xml)
    f.close()

    # run script
    xml_path = 'simulation_parameters.xml'
    # xml_path = 'test_params.xml'
    command = script + " " + xml_path + " " + output_folder
    subprocess.call(command, shell=True)

main()