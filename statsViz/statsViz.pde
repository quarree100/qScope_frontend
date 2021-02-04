// GUI
import controlP5.*;
ControlP5 cp5;
CheckBox checkbox;

// import UDP library
import hypermedia.net.*;
UDP udp;  // define the UDP object
String local_UDPAddress = "localhost";
int local_UDPin = 6155;
String stats = ""; // UDP string as received from q100viz.pde
boolean newData = false;
boolean initialized = false; //turns true once init data is received

boolean outputMetadata = false; // displays string of metadata on screen

int max_heat, max_power, max_spec_heat, max_spec_power_we, min_heat, min_power, min_spec_heat, min_spec_power_we, min_spec_power_m2, heat_mean, power_mean, spec_heat_mean, spec_power_mean_we;
float max_spec_power_m2, mean_co2, spec_power_mean_m2;

CO2_plot testPlot;

ArrayList<CO2_plot> plotsList = new ArrayList<CO2_plot>();

void setup()
{
        size(1024, 800);
        textAlign(LEFT,TOP);

        udp = new UDP(this, local_UDPin);
        // udp.log(true);
        udp.listen(true);

        // ----------------------------- controls ------------------------------
        cp5 = new ControlP5(this);
        checkbox = cp5.addCheckBox("CO2_series_checkbox")
                   .setPosition(20, height-100)
                   .setSize(20, 20)
                   // .setItemsPerRow(1)
                   // .setSpacingColumn(30)
                   // .setSpacingRow(20)
                   .addItem("toggle metadata display", 1)
        ;

        // es gibt 9 typologiezonen
        for (int i = 0; i<9; i++)
        {
                plotsList.add(new CO2_plot(0,10,0,1,150,75));

                String[] x_tick_labels = {"2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"};
                plotsList.get(i).set_x_tick_labels(x_tick_labels);
                String[] y_tick_labels = {"0", "0.25", "0.5", "0.75", "1"};
                plotsList.get(i).set_y_tick_labels(y_tick_labels);
                plotsList.get(i).set_title("Typologiezone " + (i));
        }

        // demo: fill plots with random data
        // for (CO2_plot plot : plotsList)
        // {
        //         for (int i = 0; i<11; i++)
        //         {
        //                 try {
        //                         plot.add_values(i, random(1));
        //                 }
        //                 catch (Exception e)
        //                 {
        //                         println(e);
        //                 }
        //         }
        // }

        // testPlot = new CO2_plot(0, 10, 0, 1, 400, 150);
        // testPlot.set_x_label("year");
        // testPlot.set_y_label("CO2");
        // String[] x_tick_labels = {"2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"};
        // testPlot.set_x_tick_labels(x_tick_labels);
        // String[] y_tick_labels = {"0", "0.25", "0.5", "0.75", "1"};
        // testPlot.set_y_tick_labels(y_tick_labels);
}


void draw()
{
        background(0);
        fill(255);

        drawSpiderWebDiagram(2*width/3, 1*height/3);
        textOutput();
        textAlign(RIGHT,BOTTOM);
        String minMaxData = ("max_heat \t" + max_heat + "\nmax_power \t" + max_power + "\nmax_spec_heat \t" + max_spec_heat + "\nmax_spec_power_we \t" + max_spec_power_we + "\nmax_spec_power_m2 \t" + max_spec_power_m2 + "\nmin_heat \t" + min_heat + "\nmin_power \t" + min_power + "\nmin_spec_heat \t" + min_spec_heat + "\nmin_spec_power_we \t" + min_spec_power_we + "\nmin_spec_power_m2 \t" + min_spec_power_m2);
        text(minMaxData, width-100, height-50);

        // ---------------------- display plots --------------------------------
        // column 1:
        for (int i = 0; i<4; i++)
        {
                plotsList.get(i).draw(50, 50 + (plotsList.get(i).axis_height + 70) * i);
        }
        // column 2:
        for (int i = 4; i<9; i++)
        {
                plotsList.get(i).draw(150 + plotsList.get(i).axis_width, 50 + (plotsList.get(i).axis_height + 70) * (i-4));
        }
}

void controlEvent(ControlEvent theEvent) {
        if (theEvent.isFrom(checkbox)) {
                outputMetadata = !outputMetadata;
        }
}
