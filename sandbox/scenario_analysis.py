'''Load and display all technical scenario data
The data will be used as a reference environment in the ABM
and displayed on the Q-Scope-Infoscreen
@dunland, 2022-08-17 '''

import os
from matplotlib import pyplot as plt
import pandas

print(os.getcwd())

def main():
    '''choose which of the plots to display'''
    # plot_energy_prices_separated()
    # plot_carbon_prices()
    plot_carbon_prices_separated()
    # plot_q100_prices()

######################### carbon prices ###############################
def plot_carbon_prices():
    '''display carbon price scenarios in a single line plot'''
    file = "../data/includes/csv-data_technical/carbon-prices.csv"

    df = pandas.read_csv(file).set_index('year')

    plt.figure("Carbon Prices")
    for col in df.columns:
        df.plot(
            kind='line',
            y=col,
            ax=plt.gca())

    plt.title("Carbon Prices")
    plt.ylabel("[€/g]")
    plt.show()

# separate plots:
def plot_carbon_prices_separated():
    '''display carbon price plots in separate windows'''

    file = "../data/includes/csv-data_technical/carbon-prices.csv"

    df = pandas.read_csv(file).set_index('year')

    for col in df.columns:

        plt.figure("Carbon Prices {0}".format(col))
        df.plot(
            kind='area',
            y=col,
            ax=plt.gca(),
            color='grey'
        )

        plt.gca().get_legend().remove()

    plt.ylabel("[€/g]")
    plt.show()

############################# energy prices ###########################
# sorted by type:
def plot_energy_prices_type_sorted():
    '''display energy prices in subplots, sorted by energy carrier'''
    file = "../data/includes/csv-data_technical/energy_prices-emissions.csv"

    df = pandas.read_csv(file)
    print(df)

    fig, (ax1, ax2, ax3) = plt.subplots(1,3, sharey=True)
    ax1.plot(df['year'], df['power_prices_scenario_old'],
             df['year'], df['power_prices_scenario_2021'],
             df['year'], df['power_prices_scenario_2022'])
    ax2.plot(df['year'], df['gas_prices_scenario_old'],
             df['year'], df['gas_prices_scenario_2021'],
             df['year'], df['gas_prices_scenario_2022'])
    ax3.plot(df['year'], df['oil_prices_scenario_old'],
             df['year'], df['oil_prices_scenario_2021'],
             df['year'], df['oil_prices_scenario_2022'])

    ax1.set_title('power')
    ax2.set_title('gas')
    ax3.set_title('oil')

    for ax in [ax1, ax2, ax3]:
        ax.legend(['scenario_old', 'scenario_2021', 'scenario_2022'])

    fig.canvas.set_window_title('Energy Prices (type sorted)')
    ax1.set_ylabel("[ct/kWh]??????????")
    plt.show()

# sorted by scenario:
def plot_energy_prices_scenario_sorted():
    '''display energy prices in subplots, sorted by scenario'''
    file = "../data/includes/csv-data_technical/energy_prices-emissions.csv"

    df = pandas.read_csv(file)
    print(df)

    fig, (ax1, ax2, ax3) = plt.subplots(1,3, sharey=True)
    ax1.plot(df['year'], df['power_prices_scenario_old'],
             df['year'], df['gas_prices_scenario_old'],
             df['year'], df['oil_prices_scenario_old'])
    ax2.plot(df['year'], df['power_prices_scenario_2021'],
             df['year'], df['gas_prices_scenario_2021'],
             df['year'], df['oil_prices_scenario_2021'])
    ax3.plot(df['year'], df['power_prices_scenario_2022'],
             df['year'], df['gas_prices_scenario_2022'],
             df['year'], df['oil_prices_scenario_2022'])

    ax1.set_title('scenario_old')
    ax2.set_title('scenario_2021')
    ax3.set_title('scenario_2022')

    for ax in [ax1, ax2, ax3]:
        ax.legend(['power', 'gas', 'oil'])

    fig.canvas.set_window_title('Energy Price (scenario sorted)')
    ax1.set_ylabel("[ct/kWh]??????????")
    plt.show()

# no subplots:
def plot_energy_prices_separated():
    '''export separate images for each scenario containing power price, gas price, oil price'''

    file = "../data/includes/csv-data_technical/energy_prices-emissions.csv"

    df = pandas.read_csv(file).set_index("year")

    for scenario in ['old', '2021', '2022']:
        plt.figure("Prices Scenario '{0}'".format(scenario))

        df.plot(
            kind='line',
            y=['power_prices_scenario_{0}'.format(scenario),
                'gas_prices_scenario_{0}'.format(scenario),
                'oil_prices_scenario_{0}'.format(scenario)],
            ax=plt.gca(),
            color=['#EAD41E', '#1E6FEA', '#604741']
            )

        plt.ylim((0, 70))
        plt.ylabel("ct/kWh")
        plt.xlabel("Jahr")
        plt.legend(['Strom', 'Gas', 'Öl'])
        plt.title("Energiekosten Szenario '{0}'".format(scenario))

    plt.show()


############################### q100 prices ###########################
def plot_q100_prices():
    '''plot quarree100 opex and capex'''

    file = "../data/includes/csv-data_technical/q100_prices_emissions-dummy.csv"

    df = pandas.read_csv(file).set_index("year")

    ############################## opex: ##############################
    plt.figure("Q100 Opex")
    for col in ['q100_opex_scenario1-2-3', 'q100_opex_scenario2']:
        df.plot(
            kind='line',
            y=col,
            ax=plt.gca())

    plt.ylabel("[ct/kWh]")
    plt.xlabel("Jahr")
    plt.legend(["12 ct / kWh (static)", "15-9 ct / kWh (dynamic)"])
    plt.title("Q100-Wärmeversorgung: Betriebskosten")

    ############################## capex: ##############################
    plt.figure("Q100 Capex")
    df.plot(
        kind='line',
        y=['q100_capex_scenario1-2', 'q100_capex_scenario2', 'q100_capex_scenario3'],
        ax=plt.gca())

    plt.ylabel("Zahlungen")
    plt.xlabel("Jahr")
    plt.legend(["1 payment", "2 payments", "5 payments"])
    plt.title("Q100-Wärmeversorgung: Investitionskosten")

    ############################## emissions: ##############################
    plt.figure("Q100 Emissions")
    df.plot(
        kind='line',
        y=['q100_emissions_scenario1', 'q100_emissions_scenario2', 'q100_emissions_scenario3', 'q100_emissions_scenario4'],
        ax=plt.gca())

    plt.ylabel("[g/kWh]")
    plt.xlabel("Jahr")
    plt.legend(["Constant_50 g / kWh", "Declining_Steps", "Declining_Linear", "Constant_Zero emissions"])
    plt.title("Q100-Wärmeversorgung: Investitionskosten")

    plt.show()

############################## main script ############################

if __name__ == "__main__":
    main()