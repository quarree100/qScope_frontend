import subprocess
import pandas as pd

script = '/home/dunland/opt/GAMA/headless/gama-headless.sh'
simulation_file = '/home/dunland/github/qScope/q100_abm/q100/models/qScope_ABM.gaml'
output_folder = "/home/dunland/github/qScope/q100_abm/q100/outputHeadless"

# simulation data:
final_step = 200
until = None
experiment_name = "agent_decision_making"

def compose_xml(parameters, outputs, simulation_file, finalStep=None, until=None, experiment_name=None):
    # header
    xml = ['<Experiment>']
    xml.append('  <Simulation id="1" sourcePath=' + str(simulation_file) + " "
        + "finalStep=" + str(finalStep) + " "
        + "until=" + str(until) + " "
        + "experiment=" + str(experiment_name))

    # parameters
    xml.append('  <Parameters>')
    # for row in parameters.iterrows():
    #     xml.append('  <Parameter name="{0}">{1}</Parameter>'.format(row, row[field]))


def to_xml(row, simulation_file, finalStep=None, until=None, experiment_name=None):
    # header
    xml = ['<Experiment>']
    xml.append('  <Simulation id="1" sourcePath=' + str(simulation_file) + " "
        + "finalStep=" + str(finalStep) + " "
        + "until=" + str(until) + " "
        + "experiment=" + str(experiment_name))
    xml.append('  <Parameters>')

    # parameters
    for field in row.index:
        xml.append('  <Parameter name="{0}">{1}</Parameter>'.format(field, row[field]))
    xml.append('</Parameters>')

    # outputs
    xml.append('<Outputs></Outputs>')

    # end
    xml.append('</Simulation>')
    xml.append('</Experiment>')

    return '\n'.join(xml)

def main():
    data = {'param 1': 1, 'param 2' : 'asdf'}
    df = pd.DataFrame(data, index=[0])

    outputs = pd.DataFrame(columns=['id', 'name', 'frameRate'])
    outputs.loc[len(outputs)] = ['0', 'neighborhood', '1']
    outputs.loc[len(outputs)] = ['1', 'households_income_bar', '5']

    params = pd.DataFrame(columns=['name', 'type', 'value'])
    params.loc[len(params)] = ['1', 'int', '500']
    params.loc[len(params)] = ['eeh', 'float', '0.3']
    params.loc[len(params)] = ['investment', 'int', '15123']

    compose_xml(params, outputs)

    # compose xml
    xml = '\n'.join(df.apply(to_xml, axis=1, args=(simulation_file, final_step, until, experiment_name)))
    print(xml)
    f = open('simulation_parameters.xml', 'w')
    f.write(xml)
    f.close()

    # run script
    args = "simulation_parameters.xml " + output_folder
    # subprocess.run(script, args)

main()