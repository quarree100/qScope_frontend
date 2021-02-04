// import UDP library
import hypermedia.net.*;
UDP udp;  // define the UDP object
//String local_UDPAddress = "localhost";
String local_UDPAddress = "127.0.0.1";
int local_UDPin = 5000;
String incoming_message = "";
String lastMessage = "";

void initUDP()
{
        udp = new UDP(this, local_UDPin);
        // udp.log(true);
        udp.listen(true);
}

void receive(byte[] data, String ip, int port)
{
        println("[" + hour() + "." + minute() + "." + second() + "] new message incoming: ");
        incoming_message = new String(data);
        //String[] split = split(message, "\n");
        // println(message);
        //printArray(split);
}

void decodeIncomingMessage(String decode_message, Grid grid)
{
        int cell_pointer = 0;
        int type_pointer = 0;
        int x_pointer = 0, y_pointer = 0;

        for (int i = 0; i < decode_message.length(); i++)
        {
                char c = decode_message.charAt(i);
                if (c == '[' && i > 1) // ignore first and second '['
                {
                        /* next cell: */
                        cell_pointer = (cell_pointer + 1) % (grid.squareFields * grid.squareFields);
                        x_pointer = cell_pointer % grid.squareFields;
                        y_pointer = int(cell_pointer/grid.squareFields);
                }
                else if (c >= '0' && c <= '9')
                {
                        // set values in array:
                        // grid.lego_grid[x_pointer][y_pointer][type_pointer] = int(c) - 48;
                        grid.lego_grid[x_pointer][y_pointer][type_pointer] = Character.getNumericValue(c);
                        type_pointer = (type_pointer == 0) ? 1 : 0; // 0 for ID, 1 for rotation
                }
        }
        print_lego_grid_full(grid);
}

//-------------------------------- OUTPUT DATA ---------------------------------
void composeStatsToSend()
{
        if (selectedBuildingsList.size() > 0)
        {
                stats = "Typologiezone " + selectedID + " selected. \nnumber of houses = " + selectedBuildingsList.size() + "\n ID \t | \tCO2 \n\n";
                float co2_sum = 0;
                int heat_sum = 0;
                int power_sum = 0;
                int spec_heat_sum = 0;
                int spec_power_we_sum = 0;
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


}

void sendCommand(String command, int port) {
        String dataToSend = "";
        dataToSend += command;
        udp.send( dataToSend, "localhost", port );
}

// void print_lego_grid_nicely()
// {
//   println("x\ty\tid\tr");
//   for (int x = 0; x < squareFields; x++)
//   {
//     print(x + "\t");
//     // print(y + "\t");
//     // print(id + "\t");
//     // print(r);
//     for (int y = 0; y < squareFields; y++)
//     {
//       print(y + "\t");
//       print(lego_grid[x][y][0] + "\t");
//       print(lego_grid[x][y][1] + "\t");
//       println();
//     }
//     println();
//   }
//   println();
// }

void print_lego_grid_full(Grid grid)
{
        for (int x = 0; x < grid.squareFields; x++)
        {
                for (int y = 0; y < grid.squareFields; y++)
                {
                        print(grid.lego_grid[x][y][0] + "/" + grid.lego_grid[x][y][1] + "\t");
                }
                println();
        }
        println();
}
