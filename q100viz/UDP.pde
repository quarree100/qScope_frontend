// import UDP library
import hypermedia.net.*;
UDP udp;  // define the UDP object
//String local_UDPAddress = "localhost";
String local_UDPAddress = "127.0.0.1";
int local_UDPin = 5000;
String incoming_message = "";
String lastMessage = "";

void initUDP(int local_UDPin_, String local_UDPAddress_)
{
        local_UDPin = local_UDPin_;
        local_UDPAddress = local_UDPAddress_;
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
