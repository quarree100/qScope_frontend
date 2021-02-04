class Grid
{

//----------------------------- LEGO decoding ----------------------------------
int squareFields = 22;   // number of fields on both horizontal and vertical axis on physical table
int[][][] lego_grid;   // [x][y][ID/rotation]

// ------------------------------ GIS data -------------------------------------
ArrayList<Polygon> grid_coords_list = new ArrayList<Polygon>(); // stores grid XY coordinates

// ------------------------------ graphics -------------------------------------
boolean display = false; // displays the physical TUI grid -- change via 'g'


Grid(int squareFields_)
{
        squareFields = squareFields_;
        lego_grid = new int[squareFields][squareFields][2];   // [x][y][ID/rotation]
}

//////////////////////////////////// I/O ///////////////////////////////////////
void check_incoming_message()
{
        if (incoming_message != lastMessage) decodeIncomingMessage(incoming_message, this);
        lastMessage = incoming_message;
}

/////////////////////////////////// SETUP //////////////////////////////////////
void init()
{
        // create grid XY coordinates:
        int coords_scaling = int(offscreen.height / float(squareFields));
        for (int i = 0; i < squareFields*squareFields; i++)
        {
                grid_coords_list.add(new Polygon());
                Polygon lastPolygon = grid_coords_list.get(grid_coords_list.size() - 1);

                lastPolygon.latitudes = append(lastPolygon.latitudes, int(i/squareFields) * coords_scaling);
                lastPolygon.latitudes = append(lastPolygon.latitudes, int(i/squareFields) * coords_scaling + coords_scaling);
                lastPolygon.longitudes = append(lastPolygon.longitudes, i%squareFields * coords_scaling);
                lastPolygon.longitudes = append(lastPolygon.longitudes, i%squareFields * coords_scaling + coords_scaling);
                lastPolygon.latitudes = append(lastPolygon.latitudes, int(i/squareFields) * coords_scaling);
                lastPolygon.latitudes = append(lastPolygon.latitudes, int(i/squareFields) * coords_scaling + coords_scaling);
                lastPolygon.longitudes = append(lastPolygon.longitudes, i%squareFields * coords_scaling + coords_scaling);
                lastPolygon.longitudes = append(lastPolygon.longitudes, i%squareFields * coords_scaling);
        }
        for (Polygon coord : grid_coords_list)
        {
                for (int i = 0; i<coord.longitudes.length; i++)
                {
                        println_log(coord + ":\t" + coord.longitudes[i] + "\t" + coord.latitudes[i], 2);
                }
        }

        // link gridFields to overlapping buildings:
        println_log("link griedFields to overlapping buildings..", 2);

        for (Building building : buildingsList)
        {
          int[] temp_array = new int[squareFields*squareFields];
          for (int j = 0; j<grid_coords_list.size(); j++)
          {
            Polygon grid_coord = grid_coords_list.get(j);

            for (int i = 0; i<building.polygon.latitudes.length; i++)
            {
              PVector vertex_of_building = new PVector(building.polygon.longitudes[i], building.polygon.latitudes[i]);

              if (polygon_contains_pixel(grid_coord, vertex_of_building))
              {
                temp_array[j] = j+1;
              }
            }
          }

          // get length:
          int overlaps = 0;
          for (int k = 0; k<temp_array.length; k++)
          {
            if (temp_array[k] > 0) overlaps++;
          }

          // create array with that length:
          building.contained_in_gridField = new int[overlaps];
          int n = 0;
          // fill array with entries:
          for (int k = 0; k<temp_array.length; k++)
          {
            if (temp_array[k] > 0)
            {
              building.contained_in_gridField[n] = temp_array[k];
              n++;
            }
          }

        println_log(building + ".contained_in_gridField:", 2);
        if (globalVerboseLevel >= 2) printArray(building.contained_in_gridField);
      }
}


/////////////////////////////////// RENDER /////////////////////////////////////
void drawFieldEntries(PGraphics p) // draws contents delivered from backend/UDP onto keystoned layer
{
        // ellipse(asd % 8 * gridScale + 0.5 * gridScale, int(asd/8) * gridScale + 0.5 * gridScale, gridScale, gridScale);

        int gridScale = p.height/squareFields;

        for (int x_index = 0; x_index < squareFields; x_index++)
        {
                for (int y_index = 0; y_index < squareFields; y_index++)
                {
                        int this_id = lego_grid[x_index][y_index][0];
                        int this_rot = lego_grid[x_index][y_index][1];
                        /* switch cases have to be according to the json settings (tags) from cityScoPy backend:
                           "tags": [
                           "0000000000000000", --> all black
                           "1111111111111111", --> all white
                           "1111111100000000", --> half white, half black..
                           "0011001111111111", --> read from left to right, row-wise...
                           "1100110000000000",
                           "0011001111001100",
                           "0111111111111111"
                           ], */
                        p.noStroke(); // noStroke for circles
                        p.textAlign(CENTER, CENTER);

                        // define fill colors according to id/tag:
                        if (this_id == 0) p.stroke(180);
                        if (this_id == 1) p.stroke(255);
                        if (this_id == 2) p.stroke(50,50,125);
                        if (this_id == 3) p.stroke(255, 255, 0);
                        if (this_id == 4) p.stroke(0, 255, 255);
                        if (this_id == 5) p.stroke(0, 100, 255);
                        if (this_id == 6) p.stroke(100, 255, 100);

                        // draw ellipses and squares according to tags:
                        //if (this_id >= 2)
                        if (this_id >= 0)
                        {
                                // p.ellipse(x_index * gridScale + 0.5 * gridScale, y_index * gridScale + 0.5 * gridScale, gridScale, gridScale);

                                // draw square for rotation
                                p.pushMatrix();
                                p.noFill();
                                p.strokeWeight(1);
                                // p.stroke(255, 0, 0);
                                switch(this_rot) // counter-clockwise rotation
                                {
                                case (0):
                                        // do not translate
                                        p.rect(x_index * gridScale + 0.25 * gridScale, y_index * gridScale, gridScale * 0.5, gridScale * 0.5);
                                        break;
                                case (1):
                                        p.rect(x_index * gridScale, y_index * gridScale + 0.25 * gridScale, gridScale * 0.5, gridScale * 0.5);
                                        break;
                                case (2):
                                        p.rect(x_index * gridScale + 0.25 * gridScale, y_index * gridScale + 0.5 * gridScale, gridScale * 0.5, gridScale * 0.5);
                                        break;
                                case (3):
                                        p.rect(x_index * gridScale + 0.5 * gridScale, y_index * gridScale + 0.25 * gridScale, gridScale * 0.5, gridScale * 0.5);
                                        break;
                                }
                                p.noStroke();
                                p.popMatrix();

                                // display ID
                                p.fill(0);
                                p.textSize(20);
                                p.text(this_id, x_index * gridScale + 0.5 * gridScale, y_index * gridScale + 0.5 * gridScale);
                        }
                }
        }
}

void draw_TUI_grid(PGraphics p)
{
        p.stroke(180);
        p.noFill();
        for (Polygon grid_coord : grid_coords_list)
        {
                p.beginShape();
                p.vertex(grid_coord.longitudes[0], grid_coord.latitudes[0]);
                p.vertex(grid_coord.longitudes[0], grid_coord.latitudes[1]);
                p.vertex(grid_coord.longitudes[1], grid_coord.latitudes[1]);
                p.vertex(grid_coord.longitudes[1], grid_coord.latitudes[0]);
                p.endShape();
        }
}


void select_polygons_via_TUI() // TODO: remake this and only check for each building if allocated fields change.
{
  selectedBuildingsList.clear();
  // for (Polygon grid_coord : grid_coords_list) // TODO: DO ONLY FOR GRIDS WITH CETAIN TAG!
  for (Building building: buildingsList) // iterate buildings
  {
    for (int i = 0; i<building.contained_in_gridField.length; i++) // iterate associated gridFields
    {
      int x_index = building.contained_in_gridField[i]%squareFields;
      int y_index = int(building.contained_in_gridField[i]/squareFields);
      if (lego_grid[x_index][y_index][0] != 0) // checks specific grid field
      {
        building.selected = true;
        selectedBuildingsList.add(building);
      }
      else
      {
        building.selected = false;
      }
    }
  }
}

}
