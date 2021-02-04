/* ------------------------- TIME SERIES ------------------------------------ */
// loads CO2-series and building-specific connection to power network from file

boolean do_runCO2series = false;
boolean co2series_loaded = false; // makes sure that data is only loaded once
int global_co2_array_pointer = 0; // points at co2 data to read
int co2_series_step_timer = 0;
int num_of_years_in_series;

void loadCO2series(String co2_series_file)
{
        if (!co2series_loaded)
        {
                try {
                        Table co2_series_table = loadTable(co2_series_file, "header");
                        println_log("CO2-series loaded from file " + co2_series_file, 2);
                        co2series_loaded = true;

                        // apply data to buildings:
                        int num_of_ids = 173;
                        num_of_years_in_series = co2_series_table.getRowCount() / num_of_ids;
                        println("table data: num of rows = " + co2_series_table.getRowCount() + " num_of_years_in_series = " + num_of_years_in_series);
                        for (Building building : buildingsList)
                        {
                                building.co2_series = new float[num_of_years_in_series];
                                building.connected_series = new int[num_of_years_in_series];
                        }
                        // for i in id_from_table:
                        // for (int i = 0; i < num_of_ids; i++) { // get only first year --> 173 ids
                        int co2_array_pointer = 0; // always increases at highest id
                        for (TableRow row : co2_series_table.rows())
                        {
                                // TableRow row = co2_series_table.getRow(i);
                                buildingsList.get(row.getInt("id")).co2_series[co2_array_pointer] = row.getFloat("CO2");
                                buildingsList.get(row.getInt("id")).connected_series[co2_array_pointer] = row.getInt("Anschluss");
                                println("added " + row.getFloat("CO2") + " to bulding " + row.getInt("id"));
                                if (row.getInt("id") == num_of_ids - 1) co2_array_pointer++; // increases when last id is found
                        }

                        for (Building building : buildingsList)
                        {
                                printArray_log(building.co2_series, 3);
                        }
                        // get id_from_buildings
                        // --> adopt co2, adopt connection_state

                } catch(Exception e) {
                        println("error loading co2-series. " + e);
                }
        }
}

void runCO2series()
{
        if (hour() + minute() + second() > co2_series_step_timer)
        {
                // increase step pointer
                global_co2_array_pointer++;

                // update CO2_values and connection_state:
                println_log("global_co2_array_pointer = " + global_co2_array_pointer, 3);
                if (global_co2_array_pointer == num_of_years_in_series)
                {
                        println_log("end of CO2 series reached!", 2);
                        do_runCO2series = false;
                }
                if (do_runCO2series)
                {
                        for (Building building : buildingsList)
                        {
                                building.co2 = building.co2_series[global_co2_array_pointer];
                                if (building.connected_series[global_co2_array_pointer] == 1 ) building.connected = true; // no return to "unconnected"
                                building.assignColor();
                        }
                }

                co2_series_step_timer = hour() + minute() + second() + 1; // 1 second step
                for (int i = 0; i<GIS_Data.typologiezonenList.size(); i++)
                {
                        String co2Comm = ("co2comm");
                        float co2_sum_sector = 0;
                        int sector_connections = 0;
                        // for (Building building : selected

                        for (Building building : buildingsList)
                        {
                                PVector firstVertex = new PVector(building.polygon.longitudes[0], building.polygon.latitudes[0]);
                                if (polygon_contains_pixel(GIS_Data.typologiezonenList.get(i), firstVertex))
                                {
                                        co2_sum_sector += building.co2;
                                        if (building.connected) sector_connections++;
                                }
                        }
                        //add co2
                        co2Comm = co2Comm + "\n" + GIS_Data.typologiezonenList.get(i).id + "\n" + co2_sum_sector + "\n" + sector_connections;
                        println_log(co2Comm, 2);
                        sendCommand(co2Comm, 6155);
                }
        }
}
