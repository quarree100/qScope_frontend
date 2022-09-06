import matplotlib.pyplot as plt
import pandas
import random

from buildings import buildings_df

'''exports all data for selected group buildings into one graph for total data view'''

plt.rc('font', size=18)

def main():
    grouped_energy_costs()

def grouped_emissions():
# get csv for each building in each group
    data = []
    for file in ["/home/dunland/Seafile/Medias_in_Res/q100-qScope/Data/Simulationsergebnisse/20220903-Forschungsmodell/output_20220903_13-52-02/emissions/CO2_emissions_7.32.csv", "/home/dunland/Seafile/Medias_in_Res/q100-qScope/Data/Simulationsergebnisse/20220903-Forschungsmodell/output_20220903_13-52-02/emissions/CO2_emissions_7.53.csv", "/home/dunland/Seafile/Medias_in_Res/q100-qScope/Data/Simulationsergebnisse/20220903-Forschungsmodell/output_20220903_13-52-02/emissions/CO2_emissions_7.54.csv", "/home/dunland/Seafile/Medias_in_Res/q100-qScope/Data/Simulationsergebnisse/20220903-Forschungsmodell/output_20220903_13-52-02/emissions/CO2_emissions_7.59.csv"]:
        # load from csv:
        new_df = pandas.read_csv(file)
        # # reorganize:
        # new_data = new_data.reset_index('current_date')['building_emissions']
        # new_data = new_data.rename(columns={'buildings_emissions' : idx})
        # # append to list:
        # data_df = data_df.join(new_data)
        data.append(new_df)
        # print(data_df)

    # make graph with y=list
    plt.figure(figsize=(16,9))  # inches
    x = data[0]['current_date']
    for df in data:
        plt.plot(df['current_date'], df['building_emissions'])


    df = buildings_df.sample(n=4)

    plt.xticks(rotation=270, fontsize=8)
    plt.legend(df['address'], loc="upper right")
    plt.show()

def grouped_energy_costs():
# get csv for each building in each group
    data = []
    labels = []
    for file in ["/home/dunland/github/qScope/data/outputs/output_test/energy_prices/energy_prices_7.32.csv", "/home/dunland/github/qScope/data/outputs/output_test/energy_prices/energy_prices_7.53.csv", "/home/dunland/github/qScope/data/outputs/output_test/energy_prices/energy_prices_7.55.csv", "/home/dunland/github/qScope/data/outputs/output_test/energy_prices/energy_prices_7.56.csv"]:
        # load from csv:
        new_df = pandas.read_csv(file)
        # # reorganize:
        # new_data = new_data.reset_index('current_date')['building_emissions']
        # new_data = new_data.rename(columns={'buildings_emissions' : idx})
        # # append to list:
        # data_df = data_df.join(new_data)
        data.append(new_df)

        rnd = random.randint(0, len(buildings_df.index)-1)
        labels.append(
            buildings_df.loc[buildings_df.index[rnd], 'address'] + ' - Wärme')  # TODO: add decisions
        labels.append(buildings_df.loc[buildings_df.index[rnd], 'address'] + ' - Strom')  # TODO: add decisions
        # print(data_df)

    # make graph with y=list
    plt.figure(figsize=(16,9))  # inches
    x = data[0]['current_date']
    for df in data:
        plt.plot(df['current_date'], df['building_expenses_heat'], color='#604741')
        plt.plot(df['current_date'], df['building_expenses_power'], color='#EAD41E')


    df = buildings_df.sample(n=4)

    plt.xticks(rotation=270, fontsize=8)
    plt.legend(labels, loc="upper right")
    plt.show()

main()