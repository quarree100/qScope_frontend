//-----------------------------LEGO Tiles---------------------------------------
ArrayList<Tile> tilesList = new ArrayList<Tile>(); // stores tiles with gridnumber, ID and rotation for multiple grid decoding

class Tile {
int grid_id;
int lego_id;
int rotation;
Tile(int gridNum)
{
        grid_id = gridNum;
}

}

int selectedID = int(random(9));

////////////////////////// POLYGONS FROM GIS IMPORT ////////////////////////////
ArrayList<Polygon> polygonsList = new ArrayList<Polygon>(); // stores all created polygons

class Polygon
{
float[] longitudes = new float[0];
float[] latitudes = new float[0];
int id;
String type;
String strasse;
boolean visible = true;
color col;

Polygon()
{

}

void render(PGraphics p)
{
        if (visible)
        {
                p.pushStyle();

                if (this.type == "waermezentrale")
                {
                        p.beginShape();
                        p.stroke(0);
                        p.strokeWeight(1);
                        p.fill(col);
                        for (int i=0; i<latitudes.length; i++)
                        {
                                p.vertex(longitudes[i], latitudes[i]);
                        }
                        p.endShape();
                }
                else if (this.type == "typologiezone")
                {
                        p.beginShape();
                        p.stroke(0);
                        p.strokeWeight(1);
                        p.fill(col);
                        for (int i=0; i<latitudes.length; i++)
                        {
                                p.vertex(longitudes[i], latitudes[i]);
                        }
                        p.endShape();
                }
                // if (this.type != "nahwaermenetz")
                // // if (this.type == "building")
                // {
                //         p.beginShape();
                //         // if (selected)
                //         if(true)
                //         {
                //                 p.strokeWeight(2);
                //                 p.stroke(255);
                //         }
                //         for (int i=0; i<latitudes.length; i++)
                //         {
                //                 p.fill(col);
                //                 p.vertex(longitudes[i], latitudes[i]);
                //         }
                //         p.endShape();
                //         p.noStroke();
                // }
                else if (this.type == "nahwaermenetz") // nahwaermenetz has to be treated differently, because it consists of lines
                {
                        for (int i = 1; i<latitudes.length; i++)
                        {

                                if (this.id == selectedID && globalVerboseLevel >= 2)
                                {
                                        p.fill(126, 10, 122);
                                        p.noStroke();
                                        p.ellipse(longitudes[i-1], latitudes[i-1], 20, 20);
                                }
                                p.strokeWeight(3);
                                p.stroke(col);
                                p.noFill();
                                if (globalVerboseLevel <= 2) p.line(longitudes[i-1], latitudes[i-1], longitudes[i], latitudes[i]);
                                // p.noStroke();
                                p.fill(255);
                                p.stroke(255);
                                p.textSize(10);
                                if (this.id == selectedID) p.textSize(14);
                                if (globalVerboseLevel >= 2) p.text(this.id + "." + (i-1), longitudes[i-1], latitudes[i-1] + 25);  // displays ids of nahwaermenetz
                                if (i == latitudes.length-1 && globalVerboseLevel >= 2)
                                {
                                        p.fill(126, 10, 122);
                                        p.noStroke();
                                        if (this.id == selectedID) p.ellipse(longitudes[i], latitudes[i], 20, 20);
                                        p.fill(255);
                                        p.stroke(255);
                                        p.strokeWeight(3);
                                        p.textSize(10);
                                        if (this.id == selectedID) p.textSize(14);
                                        p.text(this.id + "." + i, longitudes[i], latitudes[i] + 25); // displays ids of nahwaermenetz
                                }
                        }
                } // nahwaermenetz end
                p.noFill();
                p.popStyle();
        } // end if visible
}


} // Polygon Class end


// ------------------------- Polygon definition --------------------------------

color defineStreetColor(String tempStrasse)
{
        color tempCol = color(0, 0, 0);

        if (tempStrasse.equals("Berliner Straße"))
                tempCol = color(90, 204, 28);
        else if (tempStrasse.equals("Hamburger Straße"))
                tempCol = color(208, 72, 231);
        else if (tempStrasse.equals("Hans-Böckler-Straße"))
                tempCol = color(232, 36, 36);
        else if (tempStrasse.equals("Im Redder"))
                tempCol = color(179, 30, 146);
        else if (tempStrasse.equals("Neue Heimat"))
                tempCol = color(255, 232, 28);
        else if (tempStrasse.equals("Rüsdorfer Straße"))
                tempCol = color(31, 160, 175);
        else if (tempStrasse.equals("Stettiner Straße"))
                tempCol = color(102, 15, 133);
        return tempCol;
}

// --------------------------- Polygon interactions ----------------------------

boolean polygon_contains_pixel(Polygon poly_in, PVector pos) { //TODO: void polygon_contains_polygon
        PVector[] verts = new PVector[poly_in.latitudes.length];
        //convert polygon.lats and polygon.lons to PVector
        for (int i = 0; i != poly_in.latitudes.length; i++)
        {
                verts[i] = new PVector(poly_in.longitudes[i], poly_in.latitudes[i]);
        }

        int i, j;
        boolean c=false;
        int sides = verts.length;
        for (i=0,j=sides-1; i<sides; j=i++) {
                if (( ((verts[i].y <= pos.y) && (pos.y < verts[j].y)) || ((verts[j].y <= pos.y) && (pos.y < verts[i].y))) &&
                    (pos.x < (verts[j].x - verts[i].x) * (pos.y - verts[i].y) / (verts[j].y - verts[i].y) + verts[i].x)) {
                        c = !c;
                }
        }
        return c;
}
