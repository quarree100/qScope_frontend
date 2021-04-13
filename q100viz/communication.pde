/* Communication with statsViz.pde is assembled here.
 * → metadata of buildings etc can be compiled and sent to statsViz for statistics view
 */

class StatsViz{

  String stats; // String to be sent to statsViz

  double inf = Double.POSITIVE_INFINITY;
  int max_heat = 0, max_power = 0, max_spec_heat = 0, max_spec_power_we = 0;
  float max_spec_power_m2 = 0;

  double min_heat = inf;
  double min_power = inf;
  double min_spec_heat = inf;
  double min_spec_power_we = inf;
  double min_spec_power_m2 = inf;

  StatsViz(){}

  StatsViz(String local_UDPAddress_, int local_UDPin_)
  {
    local_UDPAddress = local_UDPAddress_; // standard:"127.0.0.1"
    local_UDPin = local_UDPin_; //standard: 5000;
  }




// set values for statistical depiction in statsViz.pde:
void evaluateMaxValues()
{

        for (Building building : buildingsList)
        {
                max_heat = (building.heat_consumption_2017 > max_heat) ? building.heat_consumption_2017 : max_heat;
                max_power = (building.e_power_consumption_2017 > max_power) ? building.e_power_consumption_2017 : max_power;
                max_spec_heat = (building.specific_heat_consumption > max_spec_heat) ? building.e_power_consumption_2017 : max_spec_heat;
                max_spec_power_we = (building.specific_power_consumption_we > max_spec_power_we) ? building.specific_power_consumption_we : max_spec_power_we;
                max_spec_power_m2 = (building.specific_power_consumption_m2 > max_spec_power_m2) ? building.specific_power_consumption_m2 : max_spec_power_m2;

                min_heat = (building.heat_consumption_2017 < min_heat) ? building.heat_consumption_2017 : min_heat;
                min_power = (building.e_power_consumption_2017 < min_power) ? building.e_power_consumption_2017 : min_power;
                min_spec_heat = (building.specific_heat_consumption < min_spec_heat) ? building.specific_heat_consumption : min_spec_heat;
                min_spec_power_we = (building.specific_power_consumption_we < min_spec_power_we) ? building.specific_power_consumption_we : min_spec_power_we;
                min_spec_power_m2 = (building.specific_power_consumption_m2 < min_spec_power_m2) ? building.specific_power_consumption_m2 : min_spec_power_m2;

        }
        // println("max_heat, max_power, max_spec_heat, max_spec_power_we, max_spec_power_m2, min_heat, min_power, min_spec_heat, min_spec_power_we, min_spec_power_m2");
        // println(max_heat, max_power, max_spec_heat, max_spec_power_we, max_spec_power_m2, min_heat, min_power, min_spec_heat, min_spec_power_we, min_spec_power_m2);

        String initComm = ("init values" + "\n" + max_heat + "\n" + max_power + "\n" + max_spec_heat + "\n" + max_spec_power_we + "\n" + max_spec_power_m2 + "\n" + min_heat + "\n" + min_power + "\n" + min_spec_heat + "\n" + min_spec_power_we + "\n" + min_spec_power_m2);
        sendCommand(initComm, 6155); // sends min and max values to statsViz.pde

}

void sendInitialString()
{
  String initComm = ("init" + "\n" + max_heat + "\n" + max_power + "\n" + max_spec_heat + "\n" + max_spec_power_we + "\n" + max_spec_power_m2 + "\n" + min_heat + "\n" + min_power + "\n" + min_spec_heat + "\n" + min_spec_power_we + "\n" + min_spec_power_m2);
  sendCommand(initComm, 6155);
}

//-------------------------------- OUTPUT DATA -------------------------------
void send_stats()
{
        if (selectedBuildingsList.size() > 0)
        {
                stats = "Typologiezone " + selectedID + " selected. \nnumber of houses = " + selectedBuildingsList.size() + "\n ID \t | \tCO2 \n\n";
                float co2_sum = 0;
                int heat_sum = 0, power_sum = 0, spec_heat_sum = 0, spec_power_we_sum = 0;
                float spec_power_m2_sum = 0;
                for (Building building : selectedBuildingsList) // TODO: new column if selectedBuildingsList > 20
                {
                        stats += nf(building.id, 3, 0);
                        stats += " \t | \t";
                        stats += nf(building.co2, 1, 3);
                        co2_sum += building.co2;
                        heat_sum += building.heat_consumption_2017;
                        power_sum += building.e_power_consumption_2017;
                        spec_heat_sum += building.specific_heat_consumption;
                        spec_power_we_sum += building.specific_power_consumption_we;
                        spec_power_m2_sum += building.specific_power_consumption_m2;
                }
                float co2_mean = co2_sum / selectedBuildingsList.size();
                float heat_mean = heat_sum / selectedBuildingsList.size();
                float power_mean = power_sum / selectedBuildingsList.size();
                float spec_heat_mean = spec_heat_sum / selectedBuildingsList.size();
                float spec_power_mean_we = spec_power_we_sum / selectedBuildingsList.size();
                float spec_power_mean_m2 = spec_power_m2_sum / float(selectedBuildingsList.size());
                stats += "\nCO2 sum \t" + nf(co2_sum, 1, 3) + "\n mean CO2-Emission \t" + nf(co2_mean, 1, 3);
                stats += "\n heat_mean\t" + heat_mean + "\n power_mean \t" + power_mean + "\n spec_heat_mean \t" + spec_heat_mean + "\n spec_power_mean_we \t" + spec_power_mean_we;
                stats += "\n spec_power_mean_m2 \t" + spec_power_mean_m2; //TODO do not display NaNs
        }
        if (stats != null)
          println_log(stats, 3); // TODO: q100_viz sends "null" before first typologiezone was selected via keyboard...
        else println_log("no Typologiezone selected. Press 1-8 to select one and print stats.", 3);
        sendCommand(stats, 6155);


}

// send data to statsViz.pde via UDP:
void sendCommand(String command, int port) {
        String dataToSend = "";
        dataToSend += command;
        udp.send( dataToSend, "localhost", port );
}

}
