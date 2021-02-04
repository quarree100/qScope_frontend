void receive( byte[] data, String ip, int port ) {  // <-- extended handler
        // get the "real" message =
        String message = new String( data );

        // println("received message: \n" + message);
        newData = true;

        String[] split = split(message, "\n");
        // printArray(split);
        if (split[0].equals("init"))
        {
                // println("init data received.");
                // println("max_heat, max_power, max_spec_heat, max_spec_power_we, max_spec_power_m2, min_heat, min_power, min_spec_heat, min_spec_power_we, min_spec_power_m2:");
                // println(max_heat, max_power, max_spec_heat, max_spec_power_we, max_spec_power_m2, min_heat, min_power, min_spec_heat, min_spec_power_we, min_spec_power_m2);

                max_heat = int(split[1]);
                max_power = int(split[2]);
                max_spec_heat = int(split[3]);
                max_spec_power_we = int(split[4]);
                max_spec_power_m2 = float(split[5]);
                min_heat = int(split[6]);
                min_power = int(split[7]);
                min_spec_heat = int(split[8]);
                min_spec_power_we = int(split[9]);
                min_spec_power_m2 = int(split[10]);

                initialized = true;
        } else if (split[0].equals("co2comm"))
        {
                /* one "co2comm" message for each sector (typologiezone)
                 * split[0] == "co2Comm"-identifier
                 * split[1] == id of sector
                 * split[2] == co2_sum_sector
                 * split[3] == sector_connections (Anzahl Anschlüsse)
                 * execute: add co2_sum_sector to graph of sector-specific graph
                 */
                println("co2Comm data received");
                println(message);
                // for (int i = 1; i<split.length; i++)
                // {
                CO2_plot plot = plotsList.get(int(split[1])-1);
                try {
                        plot.add_values(plot.values.size(), float(split[2]));
                        plot.add_values2(plot.values2.size(), float(split[3])); // TODO: make this more general for a second axis
                } catch(Exception e) {
                        println("values could not be added for plot " + split[1] + ":\n" + e);
                }
                // }

        } else {
                stats = message;
                // println("message = \n" + message);
                try
                {
                        if (int(split(split[0], " ")[1]) != selectedID)
                        {
                                selectedID = int(split(split[0], " ")[1]);
                                try {
                                        for (CO2_plot plot : plotsList)
                                        {
                                                plot.selected = false;
                                        }
                                        plotsList.get(selectedID).selected = true;
                                } catch(Exception e) {
                                        println("could not select plot. plotslist does not match input selection?\n" + e);
                                }
                        }
                }
                catch (Exception e)
                {
                        println("could not get selection ID. No sector selected?\n" + e);
                }
        }
}

void textOutput()
{
        textAlign(LEFT,TOP);
        if(newData)
        {
                String[] splitStats = split(stats, "\n");

                int x = 0;
                int y = 0;
                int ySpacing = 15;
                int xSpacing = 200;
                int lineBreak = height/15 + 4;

                int j = 0;
                if (outputMetadata)
                {
                        for (int i = 0; i<4; i++)
                        {
                                try {

                                        text(splitStats[i], x, y);
                                        y += ySpacing;
                                }
                                catch (Exception e)
                                {
                                        println(e + "\n ...probably q100viz got restarted");
                                }
                        }
                }
                if (splitStats.length > 4)
                {
                        for (int i = 4; i<splitStats.length; i++)         // get relevant data rows
                        {
                                if (i % lineBreak == 0)
                                {
                                        j++;
                                        x += xSpacing;
                                        y = 60;
                                }
                                // println("data["+i+"] = " + data[i]);
                                if (outputMetadata)
                                {

                                        fill(255);
                                        text(splitStats[i], x, y);
                                        y += ySpacing;
                                }
                                // assign zone specific stats:
                                try
                                {
                                        switch (splitStats.length-i)
                                        {
                                        case (6):
                                                mean_co2 = float(split(splitStats[i], "\t")[1]);
                                                // println(mean_co2);
                                                break;
                                        case (5):
                                                heat_mean = int(split(splitStats[i], "\t")[1]);
                                                break;
                                        case (4):
                                                power_mean = int(split(splitStats[i], "\t")[1]);
                                                break;
                                        case (3):
                                                spec_heat_mean = int(split(splitStats[i], "\t")[1]);
                                                // println(spec_heat_mean);
                                                break;
                                        case (2):
                                                spec_power_mean_we = int(split(splitStats[i], "\t")[1]);
                                                break;
                                        case (1):
                                                spec_power_mean_m2 = float(split(splitStats[i], "\t")[1]);
                                                break;

                                        }
                                } catch (Exception e)
                                {
                                        println(e + "\n ... probably q100viz got restarted?");
                                }
                        }
                }
        }

}
