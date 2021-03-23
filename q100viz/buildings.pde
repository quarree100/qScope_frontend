ArrayList<Building> buildingsList = new ArrayList<Building>(); // stores list of buildings-polygons
ArrayList<Building> selectedBuildingsList = new ArrayList<Building>(); // temporarily stores houses selected with keys 0-9, only needed for transmission to statsViz


class Building {
int id;
int osm_id;
float co2;
float[] co2_series;
color col;
color strokeCol;
boolean selected = false;

// metadata:
int heat_consumption_2017;
int e_power_consumption_2017;
int specific_heat_consumption;
int specific_power_consumption_we;
float specific_power_consumption_m2;
boolean connected = false; // ans Netz angeschlossen
int[] connected_series; //

// simulation data:
int connectionCycle; // stores moment of household connection for gama-related simulations

int[] contained_in_gridField; // = new int[squareFields*squareFields]; // stores which grid fields overlap with building

Polygon polygon;

Building(Polygon polygon_obj_init)
{
        polygon = polygon_obj_init;
}

void render(PGraphics p)
{
        p.beginShape();

        // ------------------------ stroke
        if (selected) // strong white stroke if selected
        {
                p.strokeWeight(2);
                p.stroke(245);
        }
        else if (!connected) // not selected, not connected --> grey stroke
        {
                p.strokeWeight(1);
                p.stroke(190);
        }
        else // not selected, but connected --> dark green stroke
        {
                p.strokeWeight(2);
                // p.stroke(115, 139, 53);
                p.stroke(strokeCol);
        }

        // ------------------------- fill and draw vertices
        p.fill(col);
        for (int i=0; i<polygon.latitudes.length; i++)
        {
                p.vertex(polygon.longitudes[i], polygon.latitudes[i]);
        }
        p.endShape();
        p.noStroke();
        p.noFill();
}

void assignColor() // to be run when clicked/selected via LEGO
{
        if (connected)
        {
                strokeCol = color(162, 247, 40);
        } else
        {
                color green = color(96, 205, 21);
                color red = color(213, 50, 21);
                col = lerpColor(green, red, co2);
        }
}
} // building class end

/* ------------------ GENERAL FUNCTIONS CONCERNING BUILDINGS -----------------*/
void selectBuildingsInTypo(int selBuildingsIDin)
// highlights buildings according to selected typologiezone
{
        selectedBuildingsList.clear();
        for (Polygon typologiezone : gis.typologiezonenList) //iterate typologiezonen
        {
                if (typologiezone.id == selBuildingsIDin)
                {
                        // Polygon selectedTypoZone = typologiezone;
                        for (Building building : buildingsList)
                        {
                                PVector firstVertex = new PVector(building.polygon.longitudes[0], building.polygon.latitudes[0]);
                                if (polygon_contains_pixel(typologiezone, firstVertex))
                                {
                                        building.selected = true;
                                        selectedBuildingsList.add(building);
                                }
                                else {
                                        building.selected = false;
                                }
                        }
                        break;
                }
        }
}
