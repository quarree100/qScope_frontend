import matplotlib.pyplot as plt
import pandas
import datetime

import q100viz.session as session

############################### export graphs #####################
def export_individual_graph(csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, compare_data_folder=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", label_show_iteration_round=True, figsize=(16,9), overwrite_color=None, show_legend=True):
    '''exports specified column of csv-data-file for every iteration round to graph and exports png'''

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
            print(e, "csv not found in data folders... probably the selected buildings have changed between the rounds")
            session.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")

    plt.figure(figsize=figsize)  # inches

    colors = {
        'building_household_emissions' : ['black', 'dimgray', 'darkgray', 'silver'],
        'emissions_neighborhood_accu' : ['black', 'dimgray', 'darkgray', 'silver'],
        'building_household_expenses_heat' : ['firebrick', 'darkred', 'indianred', 'lightcoral'],
        'building_household_expenses_power' : ['gold', 'khaki', 'peachpuff', 'linen']
    }
    linestyles = {
        'building_household_emissions' : '-',
        'emissions_neighborhood_accu' : '-',
        'building_household_expenses_heat' : '-',
        'building_household_expenses_power' : '--',
    }

    for col_num, column in enumerate(columns):
        # plot pre-calculated reference data:
        if compare_data_folder is not None:
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
                linewidth=3)

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
                linewidth=3)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center', fontsize=28)
    plt.title(title_, fontsize=28)
    plt.gca().set_xlabel(xlabel_, fontsize=28)
    plt.gca().set_ylabel(ylabel_, fontsize=28)
    plt.xticks(fontsize=28)
    plt.yticks(fontsize=28)
    if show_legend:
        plt.legend(loc='upper right', fontsize=28)
    else:
        plt.gca().get_legend().remove()

    plt.gca().set_ylim(bottom=0)

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

############# create reference graph from default data ################
def export_default_graph(csv_name, csv_columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", show_legend=True, figsize=(16,9)):
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

        except Exception as e:
            print(e, "... probably the selected buildings have changed between the rounds")
            session.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")

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
                linewidth=3)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center')
    plt.title(title_)
    plt.xlabel(xlabel_)
    plt.ylabel(ylabel_)
    plt.xticks(rotation=270, fontsize=18)
    plt.gca().set_ylim(bottom=0)
    if show_legend:
        plt.legend(loc='upper left')
    else:
        plt.gca().get_legend().remove()

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

################### export comparison of emissions ####################
def export_compared_emissions(buildings_groups_list, current_output_folder, outfile=None, graph_popup=False, compare_data_folder=None, figsize=(16,9)):
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
                    print(e)

                # add labels:
                decisions.append(
                    "({0}, {1}, {2})".format(
                    "s" if group_df.loc[idx, 'refurbished'] else "u",
                    group_df.loc[idx, 'connection_to_heat_grid'] if group_df.loc[idx, 'connection_to_heat_grid'] != False else "k.A.",
                    "ES" if group_df.loc[idx, 'save_energy'] else "NV")
                )
                addresses.append(group_df.loc[idx, 'address'])

    # make graph
    plt.figure(figsize=(figsize))

    for label_idx, df in enumerate(data):
        # plot:
        if compare_data_folder is not None:
            plt.plot(df['current_date'], df['compare'], color='lightgray')
        plt.plot(df['current_date'], df['building_household_emissions'], color=df['color'][label_idx])

        # annotate lines:
        group_num = df.loc[df.index[0], 'group_num']
        plt.gca().annotate(
            addresses[label_idx] + "\n" +
            decisions[label_idx],
            xy=(df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'current_date'],
                df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'building_household_emissions']),
            xytext=(df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'current_date'],
                    df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'building_household_emissions'] * 1.02),
            fontsize=12,
            horizontalalignment='left',
            color=df['color'][label_idx]
        )

    # graphics:
    plt.title("Monatliche Emissionen im Vergleich")
    plt.xlabel("Jahr")
    plt.ylabel(r'$CO_{2}$-Äquivalente (kg/Monat)')
    plt.xticks(rotation=270, fontsize=18)
    # plt.legend(addresses, bbox_to_anchor=(1,1), loc="upper left", fontsize="x-small")
    plt.tight_layout()
    plt.figtext(0.5, 0.01, "s = saniert, u = unsaniert; k.A. = kein Wärmenetzanschluss; ES = energiesparend, NV = normaler Verbrauch", wrap=False, horizontalalignment='center', fontsize="x-small")

    if graph_popup:
        plt.show()
    if outfile:
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
        if group_df is not None:
            for idx in group_df.index:
                # load from csv:
                this_csv_df = pandas.read_csv(search_in_folder + "/energy_prices/energy_prices_{0}.csv".format(idx))
                this_csv_df['current_date'] = this_csv_df['current_date'].apply(GAMA_time_to_datetime)
                this_csv_df['group_num'] = [group_num for i in this_csv_df.values]
                list_of_csv_dfs.append(this_csv_df)

                # add labels:
                decisions.append(
                    "({0}, {1}, {2})".format(
                    "s" if group_df.loc[idx, 'refurbished'] else "u",
                    group_df.loc[idx, 'connection_to_heat_grid'] if group_df.loc[idx, 'connection_to_heat_grid'] != False else "k.A.",
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
            xy=(building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(list_of_csv_dfs)+1) * group_num)], 'current_date'],
                building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(list_of_csv_dfs)+1) * group_num)], 'building_household_expenses_heat']),
            xytext=(building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(list_of_csv_dfs)+1) * group_num)], 'current_date'],
                    building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(list_of_csv_dfs)+1) * group_num)], 'building_household_expenses_heat'] * 1.02),
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
        #             building_data.loc[building_data.index[int((len(building_data.index)-1)/(len(group_data)+1) * group_num)], 'building_household_expenses_power'] * 1.02),
        #     color=rgb_to_float_tuple(session.user_colors[i]),
        #     fontsize=12,
        #     horizontalalignment='left'
        # )

    # graphics:
    # TODO: specify colors
    plt.title("Energiekosten im Vergleich")
    plt.xlabel("Jahr")
    plt.ylabel("€/Monat")
    plt.xticks(rotation=270, fontsize=18)
    plt.tight_layout()
    plt.legend(labels=['Wärme', 'Strom'], loc='upper right')
    plt.figtext(0.5, 0.01, "s = saniert, u = unsaniert; k.A. = kein Wärmenetzanschluss; ES = energiesparend, NV = normaler Verbrauch", wrap=False, horizontalalignment='center', fontsize="x-small")

    if outfile is not None:
        plt.savefig(outfile, transparent=False, bbox_inches="tight")

#################### export neighborhood total data ##################
def export_neighborhood_total_data(csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, compare_data_folder=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", label_show_iteration_round=True, figsize=(16,9)):
    '''exports specified column of csv-data-file for every iteration round to graph and exports png'''

    plt.rc('font', size=18)
    # read exported results:
    rounds_data = []

    # looks for all files with specified csv_name:
    for output_folder in data_folders:
        try:
            csv_data = pandas.read_csv(output_folder + csv_name)
            csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

            # data conversion:
            for col in columns:
                if convert_grams_to_tons:
                    csv_data[col] = csv_data[col].apply(grams_to_tons)
                elif convert_grams_to_kg:
                    csv_data[col] = csv_data[col].apply(grams_to_kg)

            rounds_data.append(csv_data)

        except Exception as e:
            print(e, "... probably the selected buildings have changed between the rounds")
            session.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")

    plt.figure(figsize=figsize)  # inches

    for col_num, column in enumerate(columns):
        # plot pre-calculated reference data:
        if compare_data_folder is not None:
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
                linewidth=3)

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
                linewidth=3)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center', fontsize=28)
    plt.title(title_, fontsize=28)
    plt.gca().set_xlabel(xlabel_, fontsize=28)
    plt.gca().set_ylabel(ylabel_, fontsize=28)
    plt.xticks(fontsize=28)
    plt.yticks(fontsize=28)
    plt.legend(loc='upper left')

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