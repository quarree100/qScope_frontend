import matplotlib.pyplot as plt
import pandas

'''exports all data for selected group buildings into one graph for total data view'''

plt.rc('font', size=18)

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

plt.xticks(rotation=270, fontsize=8)
# plt.plot(
#     kind='line',
#     x='current_date',
#     columns=[df['buildings_emissions'] for df in data],
#     ax=plt.gca(),
#     linewidth=3
# )
plt.show()
