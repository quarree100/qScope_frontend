/* ------------------------- TIME SERIES ------------------------------------ */
// loads CO2-series and building-specific connection to power network from file
class TimeSeries{


boolean running = false;
boolean series_loaded = false; // makes sure that data is only loaded once
int global_co2_array_pointer = 0; // points at co2 data to read
int co2_series_step_timer = 0;
int num_of_years_in_series;
String execution_mode; // generic or GAMA

float interval = 1; // (in seconds). There will be one step per interval
long last_interval = 0; // stores time of execution of last simulation step
int cycle = 0;
int maxCycle;


TimeSeries(){}
TimeSeries(int step_interval){
  interval = step_interval;
}
TimeSeries(String input_mode, float step_interval){
  interval = step_interval;
  execution_mode = input_mode;
}


////////////////////////////////////////////////////////////////////////////////
///////////////////////////// GENERIC DATA /////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

void run(String mode_in)
{
  if (mode_in == "GAMA" || mode_in == "gama")
  {
    run_from_gama();
  }
  else
  {
    run_generic();
  }
}

// general handler for initialization of timeSeries. if String is a path to a file, try to load it.
void load(String mode_in)
{
  if (mode_in == "GAMA")
  {
<<<<<<< HEAD
    load_from_GAMA("data/gama_data_comma.csv"); // TODO: semicolon-based parsing of data (Original ist Semikolon-separiert.)
=======
    load_from_GAMA("data/gama_data_comma.csv");
>>>>>>> 74db8d95fc43d1bc198675e1124782381e611dd2
  }
  else if (mode_in == "generic")
  {
    load_generic_CO2_series("data/fiktive_CO2_daten.csv");
  }
  else
  {
    try{
      load_generic_CO2_series(mode_in);
    } catch(Exception e)
    {
      print_log(e + "; could not load input file with generic data", 2);
    }
  }
}

void load_generic_CO2_series(String co2_series_file)
{
        if (!series_loaded)
        {
                try {
                        Table co2_series_table = loadTable(co2_series_file, "header");
                        println_log("CO2-series loaded from file " + co2_series_file, 2);
                        series_loaded = true;

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

void run_generic()
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
                        timeSeries.running = false;
                }
                if (timeSeries.running)
                {
                        for (Building building : buildingsList)
                        {
                                building.co2 = building.co2_series[global_co2_array_pointer];
                                if (building.connected_series[global_co2_array_pointer] == 1 ) building.connected = true; // no return to "unconnected"
                                building.assignColor();
                        }
                }

                co2_series_step_timer = hour() + minute() + second() + 1; // 1 second step
                for (int i = 0; i<gis.typologiezonenList.size(); i++)
                {
                        String co2Comm = ("co2comm");
                        float co2_sum_sector = 0;
                        int sector_connections = 0;
                        // for (Building building : selected

                        for (Building building : buildingsList)
                        {
                                PVector firstVertex = new PVector(building.polygon.longitudes[0], building.polygon.latitudes[0]);
                                if (polygon_contains_pixel(gis.typologiezonenList.get(i), firstVertex))
                                {
                                        co2_sum_sector += building.co2;
                                        if (building.connected) sector_connections++;
                                }
                        }
                        //add co2
                        co2Comm = co2Comm + "\n" + gis.typologiezonenList.get(i).id + "\n" + co2_sum_sector + "\n" + sector_connections;
                        println_log(co2Comm, 2);
                        statsViz.sendCommand(co2Comm, 6155);
                }
        }
}


////////////////////////////////////////////////////////////////////////////////
/////////////////////////////// GAMA API ///////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

///////////////////////////////// GAMA LOAD ////////////////////////////////////
void load_from_GAMA(String gama_series)
{
    // load csv
    Table gama_data = loadTable(gama_series, "header");

    // get last cycle. (could be any row in column "cycle", but let's pick the last..)
    maxCycle = gama_data.getRow(gama_data.getRowCount() - 1).getInt("cycle");

    // cycle rows; cycle buildings; abort when building found
    for (TableRow row : gama_data.rows())
    {
      for (Building building : buildingsList)
      {
        if (building.osm_id == row.getInt("id"))
        {
           building.connectionCycle = row.getInt("momentToConnect");
           println_log("building " + building.osm_id + "connects at cycle " + building.connectionCycle, 2);
           break;
        }
      }
    }
    println_log("Loading GAMA input file finished.", 2);
}



///////////////////////////////// GAMA RUN /////////////////////////////////////
void run_from_gama()
{
  if (millis() > last_interval + interval * 1000)
  {
    // 1. increase cycle
    cycle++;
    println_log("cycle " + cycle, 1);

    // 2. iterate buildings: cycle = connectionMoment ?
    for (Building building : buildingsList)
    {
      if (cycle == building.connectionCycle)
      {
        building.connected = true;
        building.assignColor();
        building.col = color(95, 246, 151);
      }
    }

    // 2a: yes: set building = connected

    // 3. update other metadata

    // 4. tidy up
    if (cycle > maxCycle) running = false;
    last_interval = millis();
  }
}
}
