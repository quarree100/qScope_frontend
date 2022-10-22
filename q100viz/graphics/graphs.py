import matplotlib.pyplot as plt
import pandas
import datetime

import q100viz.session as session

############################### export graphs #####################
def export_individual_graph(csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, compare_data_folder=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", label_show_iteration_round=True):
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

    plt.figure(figsize=(16, 9))  # inches

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

    it_round = 0
    for df in rounds_data:
        for col_num, column in enumerate(columns):
            # plot regular graph:
            if label_show_iteration_round:
                label_ = 'Durchlauf {0}'.format(
                    it_round+1) if labels_ == None else '{0} (Durchlauf {1})'.format(labels_[col_num], it_round+1)
            elif labels_ is not None:
                label_ = '{0}'.format(labels_[col_num])

            # lower brightness for each round:
            color_ = (
                session.quarree_colors_float[col_num % len(
                    columns)][0]/(1+it_round*0.33),  # r, float
                session.quarree_colors_float[col_num % len(
                    columns)][1]/(1+it_round*0.33),  # g, float
                session.quarree_colors_float[col_num % len(
                    columns)][2]/(1+it_round*0.33),  # b, float
            )

            # plot:
            df.plot(
                kind='line',
                x=x_,
                y=column,
                label=label_,
                color=color_,
                ax=plt.gca(),
                linewidth=3)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center')
    plt.title(title_)
    plt.xlabel(xlabel_)
    plt.ylabel(ylabel_)
    plt.xticks(rotation=270, fontsize=18)
    plt.legend(loc='upper left')

    if outfile is not None:
        plt.savefig(outfile, transparent=True, bbox_inches="tight")

def export_default_graph(csv_name, csv_columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, data_folders=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False, figtext="", line_types=None, label_show_iteration_round=True, show_legend=True):
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
            for col in csv_columns:
                if convert_grams_to_tons:
                    csv_data[col] = csv_data[col].apply(grams_to_tons)
                elif convert_grams_to_kg:
                    csv_data[col] = csv_data[col].apply(grams_to_kg)

            rounds_data.append(csv_data)

        except Exception as e:
            print(e, "... probably the selected buildings have changed between the rounds")
            session.log += ("\n%s" % e + "... probably the selected buildings have changed between the rounds")

    plt.figure(figsize=(16, 9))  # inches

    it_round = 0
    for df in rounds_data:
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
                label = '{0}'.format(labels_[col_num]),
                linewidth=3)

        it_round += 1

    plt.tight_layout()  # makes sure all objects are inside the figure boundaries
    plt.figtext(0.5, -0.1, figtext, wrap=False, horizontalalignment='center')
    plt.title(title_)
    plt.xlabel(xlabel_)
    plt.ylabel(ylabel_)
    plt.xticks(rotation=270, fontsize=18)
    if show_legend:
        plt.legend(loc='upper left')
    else:
        plt.gca().get_legend().remove()

    if outfile is not None:
        plt.savefig(outfile, transparent=True, bbox_inches="tight")

def export_combined_emissions(buildings_groups_list, current_output_folder, outfile=None, graph_popup=False, compare_data_folder=None):
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
                        print(compare_df)
                        new_df['compare'] = compare_df['building_household_emissions'].apply(grams_to_kg)
                        print(new_df)

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
    plt.figure(figsize=(16,9))  #

    print(data)

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
    plt.title("Quartiersemissionen im Vergleich")
    plt.xlabel("Jahr")
    plt.ylabel(r'Emissionen $CO_{2}$ [kg/Monat]')
    plt.xticks(rotation=270, fontsize=18)
    # plt.legend(addresses, bbox_to_anchor=(1,1), loc="upper left", fontsize="x-small")
    plt.tight_layout()
    plt.figtext(0.5, 0.01, "s = saniert, u = unsaniert; k.A. = kein Wärmenetzanschluss; ES = energiesparend, NV = normaler Verbrauch", wrap=False, horizontalalignment='center', fontsize="x-small")

    if graph_popup:
        plt.show()
    if outfile:
        plt.savefig(outfile, transparent=True, bbox_inches="tight")

def export_combined_energy_prices(current_output_folder, outfile=None, compare_data_folder=None):
    '''exports all data for selected group buildings into one graph for total data view'''

    plt.rc('font', size=18)
    colors = [
        ('seagreen', 'limegreen'),
        ('darkgoldenrod', 'gold'),
        ('steelblue', 'lightskyblue'),
        ('saddlebrown', 'sandybrown')]

    # get csv for each building in each group
    data = []
    labels = []
    compare_data = []
    for group_num, group_df in enumerate(session.buildings.list_from_groups()):
        if group_df is not None:
            for idx in group_df.index:
                # load from csv:
                new_df = pandas.read_csv(current_output_folder + "/energy_prices/energy_prices_{0}.csv".format(idx))
                new_df['current_date'] = new_df['current_date'].apply(GAMA_time_to_datetime)
                new_df['group_num'] = [group_num for i in new_df.values]
                data.append(new_df)

                labels.append(group_df.loc[idx, 'address'] + ' - Wärme')  # TODO: add decisions
                labels.append(group_df.loc[idx, 'address'] + ' - Strom')  # TODO: add decisions

                if compare_data_folder is not None:
                    comp = pandas.read_csv(compare_data_folder + '/energy_prices/energy_prices_{0}.csv'.format(idx))
                    comp['current_date'] = comp['current_date'].apply(GAMA_time_to_datetime)
                    compare_data.append(comp)

    print(compare_data)

    # make graph
    plt.figure(figsize=(16,9))  # inches

    label_idx = 0
    for i, df in enumerate(data):
        # plot pre-calculated default data of that building
        if compare_data_folder is not None:
            plt.plot(compare_data[i]['current_date'],
                compare_data[i]['building_household_expenses_heat'], color='lightgray')

        # plot heat expenses:
        plt.plot(df['current_date'],
                df['building_household_expenses_heat'], color=colors[i%len(colors)][0])

        # annotate graph:
        group_num = df.loc[df.index[0], 'group_num']
        plt.gca().annotate(
            labels[label_idx],
            xy=(df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'current_date'],
                df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'building_household_expenses_heat']),
            xytext=(df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'current_date'],
                    df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'building_household_expenses_heat'] * 1.02),
            color=colors[i%len(colors)][0],
            fontsize=12,
            horizontalalignment='left'
        )

        label_idx += 1

        # plot pre-calculated default data of that building
        if compare_data_folder is not None:
            plt.plot(compare_data[i]['current_date'],
                compare_data[i]['building_household_expenses_power'], color='lightgray')

        # plot power expenses:
        plt.plot(df['current_date'],
                df['building_household_expenses_power'], color=colors[i%len(colors)][1])


        # annotate graph
        plt.gca().annotate(
            labels[label_idx],
            xy=(df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'current_date'],
                df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'building_household_expenses_power']),
            xytext=(df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'current_date'],
                    df.loc[df.index[int((len(df.index)-1)/(len(data)+1) * group_num)], 'building_household_expenses_power'] * 1.02),
            color=colors[i%len(colors)][1],
            fontsize=12,
            horizontalalignment='left'
        )

        label_idx += 1

    # graphics:
    # TODO: specify colors
    plt.title("Energiekosten im Vergleich")
    plt.xlabel("Jahr")
    plt.ylabel("€/Monat")
    plt.xticks(rotation=270, fontsize=18)
    plt.tight_layout()

    if outfile is not None:
        plt.savefig(outfile, transparent=True, bbox_inches="tight")

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