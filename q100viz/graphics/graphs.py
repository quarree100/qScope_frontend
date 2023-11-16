import matplotlib.pyplot as plt
import pandas
import datetime

import q100viz.session as session
from q100viz.devtools import devtools as devtools

############################### export graphs #####################
def export_individual_emissions(csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, compare_data_folder=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", label_show_iteration_round=True, figsize=(16,9), overwrite_color=None, show_legend=True):
    '''exports emissions from csv-data-file for every iteration round to graph and exports png'''

    plt.rc('font', size=18)
    # read exported results:
    rounds_data = []

    max_val = 0
    # looks for all files with specified csv_name:
    for output_folder in data_folders:
        try:
            csv_data = pandas.read_csv(output_folder + csv_name)
            csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

            for col in columns:
                # data conversion:
                if convert_grams_to_tons:
                    csv_data[col] = csv_data[col].apply(grams_to_tons)
                elif convert_grams_to_kg:
                    csv_data[col] = csv_data[col].apply(grams_to_kg)
                # max value will set upper y limit:
                max_val = csv_data[col].max() if csv_data[col].max() > max_val else max_val

            rounds_data.append(csv_data)

        except Exception as e:
            print(e, "\ncsv not found in data folders... probably the selected buildings have changed between the rounds")
            devtools.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")


    plt.figure(figsize=figsize)  # inches

    colors = {
        'building_household_emissions' : ['black', 'dimgray', 'darkgray', 'silver'],
        'emissions_neighborhood_accu' : ['black', 'dimgray', 'darkgray', 'silver'],
        'building_household_expenses_heat' : ['firebrick', 'indianred','darkred',  'lightcoral'],
        'building_household_expenses_power' : ['#956b00', 'khaki', 'peachpuff', 'linen']
    }
    linestyles = {
        'building_household_emissions' : '-',
        'emissions_neighborhood_accu' : '-',
        'building_household_expenses_heat' : '-',
        'building_household_expenses_power' : '--',
    }

    for col_num, column in enumerate(columns):
        # plot pre-calculated reference data:
        if compare_data_folder is None:
            continue

        label_ = 'unverändert' if labels_ is None else '{0} (unverändert)'.format(labels_[col_num])
        compare_df = pandas.read_csv(compare_data_folder + csv_name)
        compare_df['current_date'] = compare_df['current_date'].apply(GAMA_time_to_datetime)
        for col in columns:
            if convert_grams_to_tons:
                compare_df[col] = compare_df[col].apply(grams_to_tons)
            elif convert_grams_to_kg:
                compare_df[col] = compare_df[col].apply(grams_to_kg)

        compare_df.plot(
            kind='line',
            linestyle=linestyles[column],
            x=x_,
            y=column,
            label=label_,
            color='lightgray',
            ax=plt.gca(),
            linewidth=5)

    for it_round, df in enumerate(rounds_data):
        # color = ['black', 'dimgray', 'darkgray', 'lightgray'][it_round]
        for col_num, column in enumerate(columns):
            # plot regular graph:
            if label_show_iteration_round:
                label_ = 'Runde {0}'.format(
                    it_round+1) if labels_ == None else '{0} (Runde {1})'.format(labels_[col_num], it_round+1)
            elif labels_ is not None:
                label_ = '{0}'.format(labels_[col_num])
            else:
                label_ = ""

            # plot:
            df.plot(
                kind='line',
                linestyle=linestyles[column],
                x=x_,
                y=column,
                label=label_,
                color=colors[column][len(rounds_data) - 1 - it_round] if overwrite_color is None else overwrite_color,
                ax=plt.gca(),
                linewidth=5)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center', fontsize='x-large')
    plt.title(title_, fontsize='x-large')
    plt.gca().set_xlabel(xlabel_, fontsize='x-large')
    plt.gca().set_ylabel(ylabel_, fontsize='x-large')
    plt.xticks(fontsize='x-large')
    plt.yticks(fontsize='x-large')
    if show_legend:
        plt.legend(loc='upper right', fontsize='x-large')
    else:
        plt.gca().get_legend().remove()

    plt.gca().set_ylim(bottom=0)

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

####################### individual energy expenses ####################
def export_individual_energy_expenses(building_idx, csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, compare_data_folder=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", label_show_iteration_round=True, figsize=(16,9), overwrite_color=None, show_legend=True, prepend_historic_data=False):
    '''exports energy expenses column of csv-data-file for every iteration round to graph, prepending historic energy prices. Finally, exports png'''

    plt.rc('font', size=18)
    # read exported results:
    rounds_data = []
    historic_prices = pandas.DataFrame()

    max_val = 0
    # looks for all files with specified csv_name:
    for output_folder in data_folders:
        try:
            csv_data = pandas.read_csv(output_folder + csv_name)
            csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

            for col in columns:
                # data conversion:
                if convert_grams_to_tons:
                    csv_data[col] = csv_data[col].apply(grams_to_tons)
                elif convert_grams_to_kg:
                    csv_data[col] = csv_data[col].apply(grams_to_kg)
                # max value will set upper y limit:
                max_val = csv_data[col].max() if csv_data[col].max() > max_val else max_val

                # ---------------- historic data ------------------
                if not prepend_historic_data:
                    continue

                historic_prices = pandas.read_csv("../data/data_pre-simulation/energy-prices_hh_2011-2022.csv")
                historic_prices.rename(
                    columns={
                        'Year' : 'current_date',
                        'Power' : 'power_price',
                        'Gas' : 'gas_price',
                        'Oil' : 'oil_price'
                        }, inplace=True)
                historic_prices = historic_prices[historic_prices['current_date'] < 2020]

                # historic heat:
                for energy_source in zip(['gas', 'oil', 'power'], ['Gas', 'Öl', 'Strom']):
                    if session.buildings.df.loc[building_idx, 'energy_source'] == energy_source[1]:
                        historic_prices['building_household_expenses_heat'] = \
                            historic_prices[energy_source[0]+'_price'] / 100 * session.buildings.df.loc[building_idx, 'area'] * session.buildings.df.loc[building_idx, 'spec_heat_consumption'] / 12 / session.buildings.df.loc[building_idx, 'units']

                # historic power:
                historic_prices['building_household_expenses_power'] = \
                    historic_prices['power_price'] / 100 * session.buildings.df.loc[building_idx, 'area'] * session.buildings.df.loc[building_idx, 'spec_power_consumption'] / 12 / session.buildings.df.loc[building_idx, 'units']


                csv_data = pandas.read_csv(output_folder + csv_name)
                csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

                csv_data = pandas.concat([historic_prices, csv_data])

            rounds_data.append(csv_data)

        except Exception as e:
            print(e, "\n...probably the selected buildings have changed between the rounds and the according csv could not be found")
            devtools.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")


    plt.figure(figsize=figsize)  # inches

    colors = {
        'building_household_emissions' : ['black', 'dimgray', 'darkgray', 'silver'],
        'emissions_neighborhood_accu' : ['black', 'dimgray', 'darkgray', 'silver'],
        'building_household_expenses_heat' : ['firebrick', 'indianred', 'darkred', 'lightcoral'],
        'building_household_expenses_power' : ['#956b00', 'khaki', 'peachpuff', 'linen']
    }
    linestyles = {
        'building_household_emissions' : '-',
        'emissions_neighborhood_accu' : '-',
        'building_household_expenses_heat' : '-',
        'building_household_expenses_power' : '--',
    }

    for col_num, column in enumerate(columns):
        # plot pre-calculated reference data:
        if compare_data_folder is None:
            continue

        label_ = 'unverändert' if labels_ is None else '{0} (unverändert)'.format(labels_[col_num])
        compare_df = pandas.read_csv(compare_data_folder + csv_name)
        compare_df['current_date'] = compare_df['current_date'].apply(GAMA_time_to_datetime)
        for col in columns:
            if convert_grams_to_tons:
                compare_df[col] = compare_df[col].apply(grams_to_tons)
            elif convert_grams_to_kg:
                compare_df[col] = compare_df[col].apply(grams_to_kg)

        compare_df = pandas.concat([historic_prices, compare_df])

        compare_df.plot(
            kind='line',
            linestyle=linestyles[column],
            x=x_,
            y=column,
            label=label_,
            color='lightgray',
            ax=plt.gca(),
            linewidth=5)

    for it_round, df in enumerate(rounds_data):
        for col_num, column in enumerate(columns):
            # plot regular graph:
            if label_show_iteration_round:
                label_ = 'Runde {0}'.format(
                    it_round+1) if labels_ == None else '{0} (Runde {1})'.format(labels_[col_num], it_round+1)
            elif labels_ is not None:
                label_ = '{0}'.format(labels_[col_num])
            else:
                label_ = ""

            # plot simulated prognosis:
            df.plot(
                kind='line',
                linestyle=linestyles[column],
                x=x_,
                y=column,
                label=label_,
                color=colors[column][len(rounds_data) - 1 - it_round] if overwrite_color is None else overwrite_color,
                ax=plt.gca(),
                linewidth=5)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center', fontsize='x-large')
    plt.title(title_, fontsize='x-large')
    plt.gca().set_xlabel(xlabel_, fontsize='x-large')
    plt.gca().set_ylabel(ylabel_, fontsize='x-large')
    plt.xticks(fontsize='x-large')
    plt.yticks(fontsize='x-large')
    if show_legend:
        plt.legend(loc='upper right', fontsize='x-large')
    else:
        plt.gca().get_legend().remove()

    plt.gca().set_ylim(bottom=0)

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

############# create reference graph from default data ################
def export_default_graph(csv_name, csv_columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", show_legend=True, figsize=(16,9), df_prepend_expenses=None):
    '''exports default data to graph with gray curve'''

    plt.rc('font', size=18)
    # read exported results:
    rounds_data = []

    # looks for all files with specified csv_name:
    for output_folder in data_folders:
        try:
            csv_data = pandas.read_csv(output_folder + csv_name)
            csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

            # data conversion:
            for col in csv_columns:
                if convert_grams_to_tons:
                    csv_data[col] = csv_data[col].apply(grams_to_tons)
                elif convert_grams_to_kg:
                    csv_data[col] = csv_data[col].apply(grams_to_kg)

            rounds_data.append(csv_data)

            if df_prepend_expenses is not None:
                df_prepend_expenses = df_prepend_expenses.rename(columns={
                    'year' : 'current_date',
                    'hh_heat_expenses_2000_2020' : 'building_household_expenses_heat',
                    'hh_power_expenses_2000_2020' : 'building_household_expenses_power'
                })

                df_prepend_expenses = df_prepend_expenses[df_prepend_expenses['current_date'] < 2020]

                csv_data = pandas.read_csv(output_folder + csv_name)
                csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

                csv_data = pandas.concat([df_prepend_expenses, csv_data])

        except Exception as e:
            print(e, "... probably the selected buildings have changed between the rounds")
            devtools.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")

    plt.figure(figsize=figsize)  # inches

    for it_round, df in enumerate(rounds_data):
        for col_num, column in enumerate(csv_columns):

            line_style = ['-', '--'][col_num]
            # plot:
            df.plot(
                kind='line',
                linestyle=line_style,
                x=x_,
                y=column,
                color='lightgray',
                ax=plt.gca(),
                label = '{0}'.format(labels_[col_num]) if labels_ is not None else "unverändert",
                linewidth=5)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center')
    plt.title(title_, fontsize='x-large')
    plt.gca().set_xlabel(xlabel_, fontsize='x-large')
    plt.gca().set_ylabel(ylabel_, fontsize='x-large')
    plt.xticks(fontsize='x-large')
    plt.yticks(fontsize='x-large')
    plt.gca().set_ylim(bottom=0)
    if show_legend:
        plt.legend(loc='upper left', fontsize='x-large')
    else:
        plt.gca().get_legend().remove()

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

################### export comparison of emissions ####################
def export_compared_emissions(buildings_groups_list, current_output_folder, outfile=None, compare_data_folder=None, figsize=(16,9)):
    '''exports all data for selected group buildings into one graph for total data view'''

    plt.rc('font', size=18)

    # get csv for each building in each group
    data = []
    decisions = []
    addresses = []
    for group_num, group_df in enumerate(buildings_groups_list):
        if group_df is not None:
            for idx in group_df.index:
                # load from csv:
                try:
                    new_df = pandas.read_csv(current_output_folder + "/emissions/CO2_emissions_{0}.csv".format(idx))
                    new_df['current_date'] = new_df['current_date'].apply(GAMA_time_to_datetime)
                    new_df['building_household_emissions'] = new_df['building_household_emissions'].apply(grams_to_kg)
                    new_df['color'] = [rgb_to_float_tuple(session.user_colors[group_num]) for i in new_df.values]
                    new_df['group_num'] = [group_num for i in new_df.values]

                    if compare_data_folder is not None:
                        compare_df = pandas.read_csv(compare_data_folder + '/emissions/CO2_emissions_{0}.csv'.format(idx))
                        new_df['compare'] = compare_df['building_household_emissions'].apply(grams_to_kg)

                    data.append(new_df)

                except Exception as e:
                    print("cannot create compared emissions graph", e)

                # add labels:
                decisions.append(
                    "(S={0}, A={1}, {2})".format(
                    int(group_df.loc[idx, 'refurbished']) if group_df.loc[idx, 'refurbished'] != False else 'unsaniert',
                    int(group_df.loc[idx, 'connection_to_heat_grid']) if group_df.loc[idx, 'connection_to_heat_grid'] != False else "k.A.",
                    "ES" if group_df.loc[idx, 'save_energy'] else "NV")
                )
                addresses.append(group_df.loc[idx, 'address'])

    # make graph
    plt.figure(figsize=(figsize))

    for label_idx, df in enumerate(data):
        # plot:
        if compare_data_folder is not None:
            plt.plot(df['current_date'], df['compare'], color='lightgray')
        plt.plot(df['current_date'], df['building_household_emissions'], color=df['color'][label_idx], linewidth=5)

        # annotate lines:
        group_num = df.loc[df.index[0], 'group_num']
        plt.gca().annotate(
            addresses[label_idx] + "\n" +
            decisions[label_idx],
            xy=(df.loc[df.index[int((len(df.index)-1)/(session.num_of_users) * group_num)], 'current_date'],
                df.loc[df.index[int((len(df.index)-1)/(session.num_of_users) * group_num)], 'building_household_emissions']),
            xytext=(df.loc[df.index[int((len(df.index)-1)/(session.num_of_users) * group_num)], 'current_date'],
                    df.loc[df.index[int((len(df.index)-1)/(session.num_of_users) * group_num)], 'building_household_emissions']),
            fontsize=12,
            horizontalalignment='left',
            color=df['color'][label_idx]
        )

    # graphics:
    plt.title("Monatliche Emissionen im Vergleich", fontsize='x-large')
    plt.gca().set_xlabel("Jahr", fontsize='x-large')
    plt.gca().set_ylabel(r'$CO_{2}$-Äquivalente (kg/Monat)', fontsize='x-large')
    plt.xticks(fontsize='x-large')
    plt.yticks(fontsize='x-large')
    # plt.legend(addresses, bbox_to_anchor=(1,1), loc="upper left", fontsize="small")
    plt.tight_layout()
    plt.figtext(0.5, 0.01, "ES = energiesparend, NV = normaler Verbrauch", wrap=False, horizontalalignment='center', fontsize="small")

    if outfile:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

################## neighborhood emissions vs connections ##############
def export_neighborhood_emissions_connections(connections_file, emissions_file, emissions_compare_file, outfile=None, figsize=(16,9)):
    '''creates a bar plot for the total number of connections to the heat grid with an overlaying line plot of total emissions'''

    # source data:
    df_emissions = pandas.read_csv(emissions_file)
    df_emissions['current_date'] = df_emissions['current_date'].apply(GAMA_time_to_datetime)
    df_emissions['emissions_neighborhood_total'] = df_emissions['emissions_neighborhood_total'].apply(grams_to_tons)

    df_connections = pandas.read_csv(connections_file)
    df_connections['current_date'] = df_connections['current_date'].apply(GAMA_time_to_datetime)
    df_connections['value'] = df_connections['value'] * len(session.buildings.df) / 100

    # reference data:
    df_emissions_compare = pandas.read_csv(emissions_compare_file)
    df_emissions_compare['current_date'] = df_emissions_compare['current_date'].apply(GAMA_time_to_datetime)
    df_emissions_compare['emissions_neighborhood_total'] = df_emissions_compare['emissions_neighborhood_total'].apply(grams_to_tons)

    # plot:
    fig = plt.figure(figsize=figsize)
    ax0 = plt.axes()  # all graphs shall be in the same figures
    plt.title("Quartiersemissionen und Wärmenetzanschlüsse", fontsize='x-large')

    ##################### left y-axis: ####################
    ax0.set_xlabel('Jahr', fontsize='x-large')
    plt.yticks(fontsize='x-large')
    plt.xticks(fontsize='x-large')

    barplot_green = ax0.bar(
        df_connections.iloc[::365, :]['current_date'],
        df_connections.iloc[::365, :]['value'],
        color='#00a84e',
        alpha=0.5
    )
    plt.gca().set_ylabel('Anzahl Wärmenetzanschlüsse', fontsize='x-large')
    plt.gca().set_yticks(range(0, len(session.buildings.df), 10),fontsize='x-large')

    #################### right y-axis: ####################
    ax1 = ax0.twinx()
    line_green, = ax1.plot(
        df_emissions['current_date'],
        df_emissions['emissions_neighborhood_total'],
        color='#00431f',
        linewidth=5
    )

    line_gray, = ax1.plot(
        df_emissions_compare['current_date'],
        df_emissions_compare['emissions_neighborhood_total'],
        color='lightgray',
        linewidth=5
    )
    plt.gca().set_ylabel("$CO_{2}$-Äquivalente (t)", fontsize='x-large')
    ax1.set_ylim(bottom=0)

    plt.yticks(fontsize='x-large')
    plt.legend([barplot_green, line_green, line_gray], ['Anschlüsse', "monatliche Emissionen", "monatliche Emissionen (unverändert)"], loc='lower center', fontsize='x-large')

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

##################### export energy costs comparison ##################
def export_compared_energy_costs(search_in_folder, outfile=None, compare_data_folder=None, figsize=(16,9)):
    '''exports all data for selected group buildings into one graph for total data view'''

    plt.rc('font', size=18)

    # get csv for each building in each group
    list_of_csv_dfs = []
    compare_data = []
    addresses = []
    decisions = []
    for group_num, group_df in enumerate(session.buildings.list_from_groups()):
        if group_df is None:
            continue

        for idx in group_df.index:
            # load from csv:
            this_csv_df = pandas.read_csv(search_in_folder + "/energy_prices/energy_prices_{0}.csv".format(idx))
            this_csv_df['current_date'] = this_csv_df['current_date'].apply(GAMA_time_to_datetime)
            this_csv_df['group_num'] = [group_num for i in this_csv_df.values]
            list_of_csv_dfs.append(this_csv_df)

            # add labels:
            decisions.append(
                "(S={0}, A={1}, {2})".format(
                int(group_df.loc[idx, 'refurbished']) if group_df.loc[idx, 'refurbished'] != False else 'unsaniert',
                int(group_df.loc[idx, 'connection_to_heat_grid']) if group_df.loc[idx, 'connection_to_heat_grid'] != False else "k.A.",
                "ES" if group_df.loc[idx, 'save_energy'] else "NV")
            )

            addresses.append(group_df.loc[idx, 'address'])

            if compare_data_folder is not None:
                comp = pandas.read_csv(compare_data_folder + '/energy_prices/energy_prices_{0}.csv'.format(idx))
                comp['current_date'] = comp['current_date'].apply(GAMA_time_to_datetime)
                compare_data.append(comp)

    # make graph
    plt.figure(figsize=figsize)  # inches

    for i, building_data in enumerate(list_of_csv_dfs):
        group_num = building_data.loc[building_data.index[0], 'group_num']
        # plot pre-calculated default data of that building
        if compare_data_folder is not None:
            plt.plot(compare_data[i]['current_date'],
                compare_data[i]['building_household_expenses_heat'], color='lightgray')

        # plot heat expenses:
        plt.plot(building_data['current_date'],
                building_data['building_household_expenses_heat'], color=rgb_to_float_tuple(session.user_colors[group_num]), label="Wärme")

        # annotate graph:
        plt.gca().annotate(
            addresses[i] + "\n" + decisions[i],
            xy=(building_data.loc[building_data.index[int((len(building_data.index)-1)/(session.num_of_users) * group_num)], 'current_date'],
                building_data.loc[building_data.index[int((len(building_data.index)-1)/(session.num_of_users) * group_num)], 'building_household_expenses_heat']),
            xytext=(building_data.loc[building_data.index[int((len(building_data.index)-1)/(session.num_of_users) * group_num)], 'current_date'],
                    building_data.loc[building_data.index[int((len(building_data.index)-1)/(session.num_of_users) * group_num)], 'building_household_expenses_heat']),
            color=rgb_to_float_tuple(session.user_colors[group_num]),
            fontsize=12,
            horizontalalignment='left'
        )

        # plot pre-calculated default data of that building
        if compare_data_folder is not None:
            plt.plot(compare_data[i]['current_date'],
                compare_data[i]['building_household_expenses_power'], linestyle="dashed", color='lightgray')

        # plot power expenses:
        plt.plot(building_data['current_date'],
                building_data['building_household_expenses_power'], color=rgb_to_float_tuple(session.user_colors[group_num]), linestyle='dashed', label="Strom")


        # annotate graph
        # plt.gca().annotate(
        #     addresses[i] + "\n" + decisions[i],
        #     xy=(building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(group_data)+1) * group_num)], 'current_date'],
        #         building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(group_data)+1) * group_num)], 'building_household_expenses_power']),
        #     xytext=(building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(group_data)+1) * group_num)], 'current_date'],
        #             building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(group_data)+1) * group_num)], 'building_household_expenses_power']),
        #     color=rgb_to_float_tuple(session.user_colors[i]),
        #     fontsize=12,
        #     horizontalalignment='left'
        # )

    # graphics:
    # TODO: specify colors
    plt.title("Energiekosten im Vergleich", fontsize='x-large')
    plt.gca().set_xlabel("Jahr", fontsize='x-large')
    plt.gca().set_ylabel("€/Monat", fontsize='x-large')
    plt.xticks(fontsize='x-large')
    plt.yticks(fontsize='x-large')
    plt.tight_layout()
    plt.legend(labels=['Wärme', 'Strom'], loc='upper right', fontsize='x-large')
    plt.figtext(0.5, 0.01, "ES = energiesparend, NV = normaler Verbrauch", wrap=False, horizontalalignment='center', fontsize="small")

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

#################### export neighborhood total data ##################
def export_neighborhood_total_data(csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, compare_data_folder=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", label_show_iteration_round=True, figsize=(16,9), prepend_data=None):
    '''exports specified column of csv-data-file for every iteration round to graph and exports png'''

    plt.rc('font', size=18)
    # read exported results:
    rounds_data = []

    # looks for all files with specified csv_name:
    for output_folder in data_folders:

        csv_data = pandas.read_csv(output_folder + csv_name)
        csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

        # data conversion:
        for col in columns:
            if convert_grams_to_tons:
                csv_data[col] = csv_data[col].apply(grams_to_tons)
            elif convert_grams_to_kg:
                csv_data[col] = csv_data[col].apply(grams_to_kg)

        if prepend_data is not None:
            historic_data = pandas.read_csv(prepend_data)
            historic_data.rename(
                columns={
                    'Year' : 'current_date',
                    'Power' : 'power_price',
                    'Gas' : 'gas_price',
                    'Oil' : 'oil_price'
                    }, inplace=True)
            historic_data = historic_data[historic_data['current_date'] < 2020]
            csv_data = pandas.concat([historic_data, csv_data])

        rounds_data.append(csv_data)



    plt.figure(figsize=figsize)  # inches

    for col_num, column in enumerate(columns):
        # plot pre-calculated reference data:
        if compare_data_folder is None:
            continue

        label_ = 'unverändert' if labels_ is None else '{0} (unverändert)'.format(labels_[col_num])
        compare_df = pandas.read_csv(compare_data_folder + csv_name)
        compare_df['current_date'] = compare_df['current_date'].apply(GAMA_time_to_datetime)
        for col in columns:
            if convert_grams_to_tons:
                compare_df[col] = compare_df[col].apply(grams_to_tons)
            elif convert_grams_to_kg:
                compare_df[col] = compare_df[col].apply(grams_to_kg)

        compare_df.plot(
            kind='line',
            x=x_,
            y=column,
            label=label_,
            color='lightgray',
            ax=plt.gca(),
            linewidth=5)

    colors = {
        'gas_price' : 'lightblue',
        'oil_price' : 'saddlebrown',
        'power_price' : 'gold'
    }

    for it_round, df in enumerate(rounds_data):
        for col_num, column in enumerate(columns):

            # plot regular graph:
            if label_show_iteration_round:
                label_ = 'Runde {0}'.format(
                    it_round+1) if labels_ == None else '{0} (Runde {1})'.format(labels_[col_num], it_round+1)
            elif labels_ is not None:
                label_ = '{0}'.format(labels_[col_num])

            # plot:
            df.plot(
                kind='line',
                x=x_,
                y=column,
                label=label_,
                color=colors[column],
                ax=plt.gca(),
                linewidth=5)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center', fontsize='x-large')
    plt.title(title_, fontsize='x-large')
    plt.gca().set_xlabel(xlabel_, fontsize='x-large')
    plt.gca().set_ylabel(ylabel_, fontsize='x-large')
    plt.xticks(fontsize='x-large')
    plt.yticks(fontsize='x-large')
    plt.legend(loc='upper left', fontsize='x-large')

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

def GAMA_time_to_datetime(input):
    dt_object = int(datetime.datetime.strptime(input[7:-11], '%Y-%m-%d').year)
    return(dt_object)

def grams_to_kg(val):
    return val / 1000

def grams_to_tons(val):
    return val / 1000000

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def rgb_to_float_tuple(rgb):
    return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)