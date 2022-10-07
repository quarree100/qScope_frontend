import matplotlib.pyplot as plt
import pandas
import datetime

import q100viz.session as session

############################### export graphs #####################
def export_using_columns(csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None, search_in_folders=None, outfile=None, convert_grams_to_kg=False, convert_grams_to_tons=False):
    '''exports specified column of csv-data-file for every iteration round to graph and exports png'''

    plt.rc('font', size=18)
    # read exported results:
    rounds_data = []

    # looks for all files with specified csv_name:
    for output_folder in search_in_folders:
        try:
            csv_data = (pandas.read_csv(output_folder + csv_name))
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
    it_round = 0
    for df in rounds_data:
        col_num = 0
        for column in columns:
            label_ = 'Durchlauf {0}'.format(
                it_round+1) if labels_ == None else '{0} (Durchlauf {1})'.format(labels_[col_num], it_round+1)

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

            col_num += 1

        it_round += 1

    plt.title(title_)
    plt.xlabel(xlabel_)
    plt.ylabel(ylabel_)
    plt.xticks(rotation=270, fontsize=18)
    plt.legend(loc='upper left')

    plt.savefig(outfile, transparent=True)

def export_combined_emissions(buildings_groups_list, current_output_folder, outfile=None, graph_popup=False):
    '''exports all data for selected group buildings into one graph for total data view'''

    plt.rc('font', size=18)
    colors = [
        ('seagreen', 'limegreen'),
        ('darkgoldenrod', 'gold'),
        ('steelblue', 'lightskyblue'),
        ('black', 'gray')]

    # get csv for each building in each group
    data = []
    decisions = []
    addresses = []
    for group_df in buildings_groups_list:
        if group_df is not None:
            for idx in group_df.index:
                # load from csv:
                try:
                    new_df = pandas.read_csv(current_output_folder + "/emissions/CO2_emissions_{0}.csv".format(idx))
                    new_df['current_date'] = new_df['current_date'].apply(GAMA_time_to_datetime)
                    new_df['building_emissions'] = new_df['building_emissions'].apply(grams_to_kg)
                    data.append(new_df)
                except Exception as e:
                    print(e)

                # add labels:
                decisions.append(
                    "{0}, Anschluss: {1}, {2})".format(
                    "saniert" if group_df.loc[idx, 'refurbished'] else "unsaniert",
                    group_df.loc[idx, 'connection_to_heat_grid'] if group_df.loc[idx, 'connection_to_heat_grid'] != False else "k.A.",
                    "energiesparend" if group_df.loc[idx, 'save_energy'] else "normaler Verbrauch")
                )
                addresses.append(group_df.loc[idx, 'address'])

    # make graph
    plt.figure(figsize=(16,9))  # inches

    for label_idx, df in enumerate(data):
        # plot:
        plt.plot(df['current_date'], df['building_emissions'], color=colors[label_idx%len(colors)][0])

        # annotate lines:
        plt.gca().annotate(
            decisions[label_idx],
            xy=(df.loc[df.index[len(df.index)-1], 'current_date'],
                df.loc[df.index[len(df.index)-1], 'building_emissions']),
            xytext=(df.loc[df.index[len(df.index)-1], 'current_date'],
                    df.loc[df.index[len(df.index)-1], 'building_emissions'] * 1.02),
            fontsize=12,
            horizontalalignment='right',
            color=colors[label_idx%len(colors)][0]
        )

    # graphics:
    plt.xlabel("Jahr")
    plt.ylabel(r'Emissionen $CO_{2}$ [kg/Monat]')
    plt.xticks(rotation=270, fontsize=18)
    plt.legend(addresses, bbox_to_anchor=(1,1), loc="upper left", fontsize="x-small")
    plt.tight_layout()
    # plt.annotate date of connection

    if graph_popup:
        plt.show()
    if outfile:
        plt.savefig(outfile, transparent=True)

def export_combined_energy_prices(current_output_folder, outfile):
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
    for group_df in session.buildings.list_from_groups():
        if group_df is not None:
            for idx in group_df.index:
                # load from csv:
                new_df = pandas.read_csv(current_output_folder + "/energy_prices/energy_prices_{0}.csv".format(idx))
                new_df['current_date'] = new_df['current_date'].apply(GAMA_time_to_datetime)
                data.append(new_df)

                labels.append(group_df.loc[idx, 'address'] + ' - Wärme')  # TODO: add decisions
                labels.append(group_df.loc[idx, 'address'] + ' - Strom')  # TODO: add decisions

    # make graph
    plt.figure(figsize=(16,9))  # inches

    label_idx = 0
    for i, df in enumerate(data):
        # plot heat expenses:
        plt.plot(df['current_date'],
                df['building_expenses_heat'], color=colors[i%len(colors)][0])

        # annotate graph:
        plt.gca().annotate(
            labels[label_idx],
            xy=(df.loc[df.index[len(df.index)-1], 'current_date'],
                df.loc[df.index[len(df.index)-1], 'building_expenses_heat']),
            xytext=(df.loc[df.index[len(df.index)-1], 'current_date'],
                    df.loc[df.index[len(df.index)-1], 'building_expenses_heat'] * 1.02),
            color=colors[i%len(colors)][0],
            fontsize=12,
            horizontalalignment='right'
        )

        label_idx += 1

        # plot power expenses:
        plt.plot(df['current_date'],
                df['building_expenses_power'], color=colors[i%len(colors)][1])

        # annotate graph
        plt.gca().annotate(
            labels[label_idx],
            xy=(df.loc[df.index[len(df.index)-1], 'current_date'],
                df.loc[df.index[len(df.index)-1], 'building_expenses_power']),
            xytext=(df.loc[df.index[len(df.index)-1], 'current_date'],
                    df.loc[df.index[len(df.index)-1], 'building_expenses_power'] * 1.02),
            color=colors[i%len(colors)][1],
            fontsize=12,
            horizontalalignment='right'
        )

        label_idx += 1

    # graphics:
    # TODO: specify colors
    plt.title("Energiekosten")
    plt.xlabel("Jahr")
    plt.ylabel("[€/Monat]")
    plt.xticks(rotation=270, fontsize=18)
    # plt.annotate date of connection

    plt.savefig(outfile, transparent=True)

def GAMA_time_to_datetime(input):
    dt_object = int(datetime.datetime.strptime(input[7:-11], '%Y-%m-%d').year)
    return(dt_object)

def grams_to_kg(val):
    return val / 1000

def grams_to_tons(val):
    return val / 1000000