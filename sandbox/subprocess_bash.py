import subprocess
import pandas as pd

script = '/home/dunland/opt/GAMA/headless/gama-headless.sh'
simulation_file = '/home/dunland/github/qScope/q100_abm/q100/models/qScope_ABM.gaml'
output_folder = "/home/dunland/github/qScope/q100_abm/q100/outputHeadless"

# simulation data:
final_step = 200
until = None
experiment_name = "agent_decision_making"


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