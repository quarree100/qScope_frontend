import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import controlP5.*; 
import hypermedia.net.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class statsViz extends PApplet {

// GUI

ControlP5 cp5;
CheckBox checkbox;

// import UDP library

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

public void setup()
{
        
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


public void draw()
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

public void controlEvent(ControlEvent theEvent) {
        if (theEvent.isFrom(checkbox)) {
                outputMetadata = !outputMetadata;
        }
}
public void receive( byte[] data, String ip, int port ) {  // <-- extended handler
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

                max_heat = PApplet.parseInt(split[1]);
                max_power = PApplet.parseInt(split[2]);
                max_spec_heat = PApplet.parseInt(split[3]);
                max_spec_power_we = PApplet.parseInt(split[4]);
                max_spec_power_m2 = PApplet.parseFloat(split[5]);
                min_heat = PApplet.parseInt(split[6]);
                min_power = PApplet.parseInt(split[7]);
                min_spec_heat = PApplet.parseInt(split[8]);
                min_spec_power_we = PApplet.parseInt(split[9]);
                min_spec_power_m2 = PApplet.parseInt(split[10]);

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
                CO2_plot plot = plotsList.get(PApplet.parseInt(split[1])-1);
                try {
                        plot.add_values(plot.values.size(), PApplet.parseFloat(split[2]));
                        plot.add_values2(plot.values2.size(), PApplet.parseFloat(split[3])); // TODO: make this more general for a second axis
                } catch(Exception e) {
                        println("values could not be added for plot " + split[1] + ":\n" + e);
                }
                // }

        } else {
                stats = message;
                println("message = \n" + message);
                try
                {
                        if (PApplet.parseInt(split(split[0], " ")[1]) != selectedID)
                        {
                                selectedID = PApplet.parseInt(split(split[0], " ")[1]);
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

public void textOutput()
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
                                                mean_co2 = PApplet.parseFloat(split(splitStats[i], "\t")[1]);
                                                // println(mean_co2);
                                                break;
                                        case (5):
                                                heat_mean = PApplet.parseInt(split(splitStats[i], "\t")[1]);
                                                break;
                                        case (4):
                                                power_mean = PApplet.parseInt(split(splitStats[i], "\t")[1]);
                                                break;
                                        case (3):
                                                spec_heat_mean = PApplet.parseInt(split(splitStats[i], "\t")[1]);
                                                // println(spec_heat_mean);
                                                break;
                                        case (2):
                                                spec_power_mean_we = PApplet.parseInt(split(splitStats[i], "\t")[1]);
                                                break;
                                        case (1):
                                                spec_power_mean_m2 = PApplet.parseFloat(split(splitStats[i], "\t")[1]);
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
int selectedID = 0; // is changed with UDP message

class CO2_plot
{
// ---------------------------------- data
float x_max, x_min, y_max, y_min;
float y2_max = 0, y2_min = 0;
int axis_width; // visual dimensions, should not be changed
int axis_height;
PVector position;
int number_of_xticks = 10;
int number_of_yticks = 5;
String x_label = "", y_label = "";
String title = "";
String[] x_tick_labels, y_tick_labels;
String[] y2_tick_labels;

boolean selected = false;

ArrayList<PVector> values = new ArrayList<PVector>();
ArrayList<PVector> values2 = new ArrayList<PVector>(); // TODO: conclude all values in one list of lists

// ----------------------------------- style
// determines style of graph display
int LINES = 0, POINTS = 1, BARPLOT = 2;
int drawMode = BARPLOT;

int axisColor = color(255, 255, 255);
int pointsColor = color(47, 169, 222);

// create plot with values only
CO2_plot(float x_min_in, float x_max_in, float y_min_in, float y_max_in)
{
        x_max = x_max_in;
        x_min = x_min_in;
        y_max = y_max_in;
        y_min = y_min_in;

        println(y_max);

}

// create plots with values and dimensions
CO2_plot(float x_min_in, float x_max_in, float y_min_in, float y_max_in, int axis_width_in, int axis_height_in)
{
        x_max = x_max_in;
        x_min = x_min_in;
        y_max = y_max_in;
        y_min = y_min_in;

        axis_width = axis_width_in;
        axis_height = axis_height_in;

        println(y_max);

}

public void draw(int x, int y)
/* x and y are upper left boundary,
 * axis_width and axis_height are lower right graph boundary
 */
{
        float x_tick_spacer = axis_width / PApplet.parseFloat(number_of_xticks);
        float y_tick_spacer = axis_height / PApplet.parseFloat(number_of_yticks);
        // ---------------------------------- box around graph if selected
        if (selected)
        {
                stroke(150);
                noFill();
                rectMode(CORNER);
                rect(x - 35, y-10, axis_width + 70, axis_height + 70);
        }
        /* -------------------------- DRAW VALUES --------------------------- */
        // fill(255,0,0); // displays x and y untranslated
        // ellipse(x,y,20,20); // displays x and y untranslated
        pushMatrix();
        translate(x, y);
        // ellipse(this.axis_width, this.axis_height, 10, 10); // displays lower right boundaries
        try {
                if (drawMode == POINTS) {
                        for (PVector value : values)
                        {
                                fill(pointsColor);
                                noStroke();
                                ellipse(value.x * x_tick_spacer, axis_height - value.y * axis_height, 5, 5);
                        }
                }

                else if (drawMode == LINES)
                {
                        for (int i = 1; i<values.size(); i++)
                        {
                                stroke(pointsColor);
                                line(values.get(i).x * x_tick_spacer, axis_height - values.get(i).y * (axis_height / y_max), values.get(i-1).x * x_tick_spacer, axis_height - values.get(i-1).y * (axis_height / y_max));
                        }
                }

                else if (drawMode == BARPLOT)
                {
                        for (int i = 1; i<values.size(); i++)
                        {
                                stroke(150);
                                fill(pointsColor);
                                rectMode(CORNERS);
                                rect(values.get(i-1).x * x_tick_spacer, axis_height - values.get(i-1).y * (axis_height / y_max), values.get(i).x * x_tick_spacer, axis_height);
                        }
                }
                // connections TODO: make this more general (2nd axis plot)
                for (int i = 1; i<values.size(); i++)
                {
                        strokeWeight(3);
                        stroke(219, 117, 22);
                        line(values2.get(i).x * x_tick_spacer, axis_height - values2.get(i).y * (axis_height / y_max), values2.get(i-1).x * x_tick_spacer, axis_height - values2.get(i-1).y * (axis_height / y_max));
                        strokeWeight(1);
                }

        } catch(Exception e) {
                println(e + ".. probably no values in graph.");
        }
        popMatrix();
        // ---------------------------------- axes
        stroke(axisColor);
        line(x, y, x, y+axis_height); // left y-axis
        line(x, y+axis_height, x+axis_width, y+axis_height); // lower x-axis

        /* ---------------------------- TICKS --------------------------------*/
        // ------------------------------ ticks:
        for (int i = 0; i<number_of_xticks; i++)
        {
                float tickx = x + i * x_tick_spacer;
                float ticky = y+axis_height;
                stroke(axisColor);
                if (i > 0) line(tickx, ticky+2, tickx, ticky-2);

                // ------------------------------- tick labels:
                pushMatrix();
                translate(tickx, ticky);
                rotate(radians(90));
                textAlign(LEFT, CENTER);
                textSize(11);
                try {
                        fill(245);
                        text(x_tick_labels[i], 10, 0);
                } catch(Exception e) {
                        println("could not display ticks:\n" + e + "\n Probably amount of ticks and labels are not equal..");
                }
                popMatrix();
        }

        // ----------------------------- y-ticks
        for (int i = 0; i<number_of_yticks; i++)
        {
                float tickx = x;
                float ticky = y + axis_height - i * y_tick_spacer;
                stroke(axisColor);
                if (i > 0) line(tickx-2, ticky, tickx+2, ticky);

                // ------------------------------- tick labels:
                textAlign(RIGHT, CENTER);
                textSize(11);
                try {
                        text(y_tick_labels[i], tickx - 5, ticky);
                } catch(Exception e) {
                        println("could not display ticks:\n" + e + "\n Probably amount of ticks and labels are not equal..");
                }
        }

        /* -------------------------- AXIS LABELS --------------------------- */
        textAlign(CENTER,BOTTOM);
        text(x_label, x + axis_width/2, y + axis_height + 50);
        textAlign(RIGHT,CENTER);
        pushMatrix();
        translate(x - 40, y + axis_height / 2);
        rotate(radians(270));
        // text(y_label, x - 10, y + axis_height / 2);
        text(y_label, 0, 0);
        popMatrix();

        /* ---------------------------- TITLE ------------------------------- */
        pushMatrix();
        translate(x, y);
        textAlign(CENTER,CENTER);
        text(title, axis_width / 2, axis_height + 50);
        popMatrix();
}

public void set_ticks(int number_of_xticks_in, int number_of_yticks_in)
{
        number_of_xticks = number_of_xticks_in;
        number_of_yticks = number_of_yticks_in;
}

public void set_x_tick_labels(String[] x_tick_labels_in)
{
        x_tick_labels = x_tick_labels_in;
        number_of_xticks = x_tick_labels.length;
}

public void set_y_tick_labels(String[] y_tick_labels_in)
{
        y_tick_labels = y_tick_labels_in;
        number_of_yticks = y_tick_labels.length;
}

public void set_x_label(String x_label_in)
{
        x_label = x_label_in;
}

public void set_y_label(String y_label_in)
{
        y_label = y_label_in;
}

public void add_values(float x_value, float y_value)
{
        values.add(new PVector(x_value, y_value));
        println(" added value " + values.get(values.size() - 1).x + " " + values.get(values.size() - 1).y);
        if (y_value > y_max)
        {
                y_max = y_value;
                println("new y_max = " + y_max);
                update_tick_labels();
        }
        // if (x_value > x_max)
        // {
        //   x_max = x_value;
        //   // println("new x_max = " + x_max);
        //   update_tick_labels();
        // }
}

public void add_values2(float x_value, float y_value)
{
        values2.add(new PVector(x_value, y_value));
        println(" added value " + values2.get(values2.size() - 1).x + " " + values2.get(values2.size() - 1).y);
        if (y_value > y2_max)
        {
                y2_max = y_value;
                println("new y_max = " + y2_max);
                update_tick_labels2();
        }
        // if (x_value > x_max)
        // {
        //   x_max = x_value;
        //   // println("new x_max = " + x_max);
        //   update_tick_labels();
        // }
}

public void update_tick_labels()
{
        for (int tick_pos = 0; tick_pos < y_tick_labels.length; tick_pos++)
        {
                float tick_as_float = (y_max / axis_height) * number_of_yticks * tick_pos;
                // println("y: tick_as_float = " + tick_as_float);
                y_tick_labels[tick_pos] = nf(tick_as_float, 0, 2);
        }
        // for (int tick_pos = 0; tick_pos < x_tick_labels.length; tick_pos++)
        // {
        //   float tick_as_float = ((x_max/axis_height) / number_of_xticks) * tick_pos;
        //   println("x: tick_as_float = " + tick_as_float);
        //   x_tick_labels[tick_pos] = str(tick_as_float);
        // }
}

public void update_tick_labels2() // TODO: make this more general for second axis
{
        for (int tick_pos = 0; tick_pos < y2_tick_labels.length; tick_pos++)
        {
                float tick_as_float = (y2_max / axis_height) * number_of_yticks * tick_pos;
                // println("y: tick_as_float = " + tick_as_float);
                y2_tick_labels[tick_pos] = nf(tick_as_float, 0, 2);
        }
        // for (int tick_pos = 0; tick_pos < x_tick_labels.length; tick_pos++)
        // {
        //   float tick_as_float = ((x_max/axis_height) / number_of_xticks) * tick_pos;
        //   println("x: tick_as_float = " + tick_as_float);
        //   x_tick_labels[tick_pos] = str(tick_as_float);
        // }
}

public void set_title(String title_in)
{
        title = title_in;
}

} // plot class end
// spiderweb diagram

public void drawSpiderWebDiagram(int x, int y)
{
  if (initialized)
  {
        float radius = 300;
        PVector webCenter = new PVector(x,y);
        PVector v = new PVector(x,y);
        PVector vecHeatCons = new PVector(x,y);
        PVector vecPowCons = new PVector(x,y);
        PVector vecSpecHeatCons = new PVector(x,y);
        PVector vecSpecPowCons_we = new PVector(x,y);
        PVector vecSpecPowCons_m2 = new PVector(x,y);
        PVector vecCO2mean = new PVector(x,y);

        v.set(cos(radians(60))*(PApplet.parseFloat(heat_mean) / PApplet.parseFloat(max_heat))*radius, sin(radians(60))*(PApplet.parseFloat(heat_mean) / PApplet.parseFloat(max_heat))*radius);
        // println(cos(radians(60)) + " " + (float(heat_mean) / float(max_heat))*radius + "\t" +  sin(radians(60)) + " " + (float(heat_mean) / float(max_heat))*radius);
        vecHeatCons.add(v);
        v.set(cos(radians(120))*(PApplet.parseFloat(power_mean) / PApplet.parseFloat(max_power))*radius, sin(radians(120))*(PApplet.parseFloat(power_mean) / PApplet.parseFloat(max_power))*radius);
        vecPowCons.add(v);
        v.set(cos(radians(180))*(PApplet.parseFloat(spec_heat_mean) / 800)*radius, sin(radians(180))*(PApplet.parseFloat(spec_heat_mean) / 800)*radius);
        // println(cos(radians(180)) + " " + (float(spec_heat_mean) / float(max_spec_heat)));
        vecSpecHeatCons.add(v);
        v.set(cos(radians(240))*(PApplet.parseFloat(spec_power_mean_we) / PApplet.parseFloat(max_spec_power_we))*radius, sin(radians(240))*(PApplet.parseFloat(spec_power_mean_we) / PApplet.parseFloat(max_spec_power_we))*radius);
        vecSpecPowCons_we.add(v);
        v.set(cos(radians(300))*((spec_power_mean_m2) / (max_spec_power_m2))*radius, sin(radians(300))*((spec_power_mean_m2) / (max_spec_power_m2))*radius);
        vecSpecPowCons_m2.add(v);
        v.set(cos(radians(360))*(mean_co2)*radius/2, sin(radians(360))*(mean_co2)*radius/2);
        // println(cos(radians(360)) + " " + mean_co2 * radius + " " + sin(radians(360)));
        vecCO2mean.add(v);


        fill(0);
        strokeWeight(1);
        ellipse(webCenter.x, webCenter.y, radius, radius);
        // rect(webCenter.x, webCenter.y, radius, radius);
        fill(color(172, 172, 172, 50));
        ellipse(webCenter.x, webCenter.y, 3*radius/4, 3*radius/4);
        fill(0);
        ellipse(webCenter.x, webCenter.y, radius/2, radius/2);
        fill(color(172, 172, 172, 50));
        ellipse(webCenter.x, webCenter.y, radius/4, radius/4);

        //data vectors
        fill(255);
        stroke(183, 214, 226);
        strokeWeight(1);
        line(webCenter.x, webCenter.y, x+cos(radians(60))*radius/2, y+sin(radians(60))*radius/2);
        line(webCenter.x, webCenter.y, x+cos(radians(120))*radius/2, y+sin(radians(120))*radius/2);
        line(webCenter.x, webCenter.y, x+cos(radians(180))*radius/2, y+sin(radians(180))*radius/2);
        line(webCenter.x, webCenter.y, x+cos(radians(240))*radius/2, y+sin(radians(240))*radius/2);
        line(webCenter.x, webCenter.y, x+cos(radians(300))*radius/2, y+sin(radians(300))*radius/2);
        line(webCenter.x, webCenter.y, x+cos(radians(360))*radius/2, y+sin(radians(360))*radius/2);

        // intervectoral lines
        beginShape();
        stroke(183, 214, 226);
        strokeWeight(3);
        fill(197, 212, 218, 70);
        vertex(vecHeatCons.x, vecHeatCons.y);
        vertex(vecPowCons.x, vecPowCons.y);
        vertex(vecSpecHeatCons.x ,vecSpecHeatCons.y);
        vertex(vecSpecPowCons_we.x, vecSpecPowCons_we.y);
        vertex(vecSpecPowCons_m2.x, vecSpecPowCons_m2.y);
        vertex(vecCO2mean.x, vecCO2mean.y);
        vertex(vecHeatCons.x, vecHeatCons.y);
        endShape();
        strokeWeight(1);

        // line legend
        textAlign(CENTER,CENTER);
        fill(255);
        text("heat_mean", x+cos(radians(60))*radius/2, y+sin(radians(60))*radius/2);
        text("power_mean", x+cos(radians(120))*radius/2, y+sin(radians(120))*radius/2);
        text("spec_heat_mean", x+cos(radians(180))*radius/2, y+sin(radians(180))*radius/2);
        text("spec_power_mean_we", x+cos(radians(240))*radius/2, y+sin(radians(240))*radius/2);
        text("spec_power_mean_m2", x+cos(radians(300))*radius/2, y+sin(radians(300))*radius/2);
        text("co2_mean", x+cos(radians(360))*radius/2, y+sin(radians(360))*radius/2);
      }
}
  public void settings() {  size(1024, 800); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "statsViz" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
