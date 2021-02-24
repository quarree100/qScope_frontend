// subclass of GIS for the region to be displayed
class Area{
  // get these coordinates from GIS map:
  int lonMin; // 1013137; //9.0975364; // y = 0
  int lonMax; // 1013901; //9.1143553; // height
  int latMin; // 7206217; //54.1876916; // x = 0
  int latMax; // 7207334; //54.1988598; // width
  int lonDiff;
  int latDiff;
  float resoX;

  Area(){}
}


class GIS
{
ArrayList<Polygon> typologiezonenList = new ArrayList<Polygon>();   // stores list of Typologiezonen
ArrayList<Polygon> nahwaermeList = new ArrayList<Polygon>();   // list of all sections in Nahwärmenetz
ArrayList<Node> nahwaermeMesh = new ArrayList<Node>();   // global invisibile Nahwärmenetz for movement of FX

// -------------- coordinate reference system information ----------------------
int crs = 3857; // define coordinate reference systeme. Will be used to load table and draw shapes. so far: crs=3857

Area area = new Area();

GIS(int lon_min, int lon_max, int lat_min, int lat_max){
  area.lonMin = lon_min;
  area.lonMax = lon_max;
  area.latMin = lat_min;
  area.latMax = lat_max;

  area.lonDiff = area.lonMax - area.lonMin;
  area.latDiff = area.latMax - area.latMin;
  area.resoX = float(area.lonDiff)/area.latDiff;

}





///////////////////////// LOAD EXTERNAL DATA FROM CSVs /////////////////////////
////////////////////////////////////////////////////////////////////////////////

// ----------------------- coordinate system conversions -----------------------
float[] convertToXY_epsg3857(String tempLon, String tempLat, PGraphics p)
{
        int lon = int(tempLon);
        int lat = int(tempLat);
        int latMin = area.latMin;
        int latMax = area.latMax;
        int lonMin = area.lonMin;
        int lonMax = area.lonMax;
        float resoX = area.resoX;

        //relative x,y
        float tempY = p.height - (float(lat - latMin) / float(latMax - latMin) * p.height); // TODO: leichter mit map()?
        float tempX = resoX * (float(lon - lonMin) / float(lonMax - lonMin) * p.width);

        // apply rotation, if set:
        // TODO: apply other rotations as well
        if (rotationDegrees == 270) // switches lat and lon
        {
                tempX = p.width * (float(latMax - lat) / float(latMax - latMin));
                tempY = p.height * float(lonMax - lon) / float(lonMax - lonMin);
        }
        else if (rotationDegrees == 90) // switches lat and lon and focuses on residual diff (val - valMin)
        {
                tempX = p.width * (float(lat - latMin) / float(latMax - latMin));
                tempY = p.height * float(lon - lonMin) / float(lonMax - lonMin);
        }

        float[] vals = {
                tempY, tempX
        };
        return vals;
}

///////////////////////////////// load datasets ////////////////////////////////

// ------------------------------ Typologiezonen -------------------------------
void load_typologiezonen()
{
        Table typologiezonen = loadTable("data/typoTable.csv", "header");
        for (TableRow row: typologiezonen.rows())
        {
                polygonsList.add(new Polygon());
                Polygon lastPolygon = polygonsList.get(polygonsList.size()-1);
                typologiezonenList.add(lastPolygon);
                lastPolygon.visible = false;
                lastPolygon.id = row.getInt("id");//pass id
                lastPolygon.type = "typologiezone";
                lastPolygon.col = color(123, 201, 230, 50);

                String[] lats = split(row.getString("lats"), ' '); // making list out of POLYGON geometry
                String[] lons = split(row.getString("lons"), ' ');

                for (int i = 0; i<lats.length-1; i++)
                {
                        String latString = split(lats[i], ".")[0]; // lats[0] = ganze zahl; lats[1] = dezimalstellen //using epsg3857 with [metres] --> use integer (pre-comma)
                        // fill String with zeros, until 7 digits long
                        for (int j = 0; j < 7-lats[0].length(); j++)
                        {
                                latString = latString + "0";
                        }

                        String lonString = split(lons[i], ".")[0];
                        for (int j = 0; j < 7-lons[0].length(); j++)
                        {
                                lonString = lonString + "0";
                        }
                        float y = convertToXY_epsg3857(lonString, latString, offscreen)[0];
                        float x = convertToXY_epsg3857(lonString, latString, offscreen)[1];
                        lastPolygon.latitudes = append(lastPolygon.latitudes, y);
                        lastPolygon.longitudes = append(lastPolygon.longitudes, x);
                }
        }
        println(typologiezonen.getRowCount() + " polygons for typologiezonen added.");
//  polygonsList.get(polygonsList.size() - 4).col = superColor; // for demonstration only
}

// --------------------------------- buildings ---------------------------------
void load_buildings() // loads GIS shapefiles and creates polygon objects
{
  boolean load_buildingSpecific_data = true;
        switch (crs)
        {
        case 3857:
                Table buildingsTable = loadTable("data/buildings.csv", "header");
                for (TableRow row: buildingsTable.rows())
                {
                        polygonsList.add(new Polygon());
                        Polygon lastPolygon = polygonsList.get(polygonsList.size()-1);
                        buildingsList.add(new Building(lastPolygon));
                        Building lastBuilding = buildingsList.get(buildingsList.size()-1);
                        lastPolygon.id = row.getInt("id");//pass id
                        lastBuilding.id = row.getInt("id");
                        lastBuilding.osm_id = row.getInt("osm_id");
                        // lastPolygon.type = "strasse";
                        lastPolygon.strasse = row.getString("Straße");
                        try {
                                lastBuilding.heat_consumption_2017 = int(row.getFloat("Wärmeverbrauch 2017 [kWh]"));
                                lastBuilding.e_power_consumption_2017 = row.getInt("Stromverbrauch 2017 [kWh]");
                                lastBuilding.specific_heat_consumption = row.getInt("Spez. Wärmeverbr. [kWh/m²]");
                                lastBuilding.specific_power_consumption_we= row.getInt("Spez. Stromverbr. [kWh/WE]");
                                lastBuilding.specific_power_consumption_m2= row.getFloat("Spez. Stromverbr. [kWh/m²]");
                                //println("lastPolygon.strasse = " + lastPolygon.strasse);
                        } catch(Exception e) {
                          load_buildingSpecific_data = false;
                        }                        lastBuilding.col = defineStreetColor(lastPolygon.strasse); // allocates color according to street

                        String[] lats = split(row.getString("lats"), ' '); // making list out of POLYGON geometry
                        String[] lons = split(row.getString("lons"), ' ');

                        for (int i = 0; i<lats.length-1; i++)
                        {
                                String latString = split(lats[i], ".")[0]; // lats[0] = ganze zahl; lats[1] = dezimalstellen //using epsg3857 with [metres] --> use integer (pre-comma)
                                // fill String with zeros, until 7 digits long
                                for (int j = 0; j < 7-lats[0].length(); j++)
                                {
                                        latString = latString + "0";
                                }

                                String lonString = split(lons[i], ".")[0];
                                for (int j = 0; j < 7-lons[0].length(); j++)
                                {
                                        lonString = lonString + "0";
                                }
                                float y = convertToXY_epsg3857(lonString, latString, offscreen)[0];
                                float x = convertToXY_epsg3857(lonString, latString, offscreen)[1];
                                lastPolygon.latitudes = append(lastPolygon.latitudes, y);
                                lastPolygon.longitudes = append(lastPolygon.longitudes, x);
                        }
                }
                break;
        }
        println_log(buildingsList.size() + " polygons for buildings added.", 1);
        if (!load_buildingSpecific_data) println_log("building-specific data could not be loaded." ,1);
}

// -------------------------------- Waermezentrale -----------------------------
void load_waermezentrale()
{
        Table waermezentrale = loadTable("data/waerme_zentrale.csv", "header");
        for (TableRow row : waermezentrale.rows())
        {
                polygonsList.add(new Polygon());
                Polygon lastPolygon = polygonsList.get(polygonsList.size()-1);
                lastPolygon.type = "waermezentrale";
                lastPolygon.id = row.getInt("id");//pass id
                lastPolygon.col = color(252, 137, 0);
                println_log("Wärmezentrale has Polygon id " + (polygonsList.size() - 1), 2);

                String[] lats = split(row.getString("lats"), ' '); // making list out of POLYGON geometry
                String[] lons = split(row.getString("lons"), ' ');

                for (int i = 0; i<lats.length-1; i++)
                {
                        String latString = split(lats[i], ".")[0]; // lats[0] = ganze zahl; lats[1] = dezimalstellen //using epsg3857 with [metres] --> use integer (pre-comma)
                        // fill String with zeros, until 7 digits long
                        for (int j = 0; j < 7-lats[0].length(); j++)
                        {
                                latString = latString + "0";
                        }

                        String lonString = split(lons[i], ".")[0];
                        for (int j = 0; j < 7-lons[0].length(); j++)
                        {
                                lonString = lonString + "0";
                        }
                        float y = convertToXY_epsg3857(lonString, latString, offscreen)[0];
                        float x = convertToXY_epsg3857(lonString, latString, offscreen)[1];
                        lastPolygon.latitudes = append(lastPolygon.latitudes, y);
                        lastPolygon.longitudes = append(lastPolygon.longitudes, x);

                }

        }
        println(waermezentrale.getRowCount() + " polygons for waermezentrale added.");
}


// -------------------------------- Nahwaermenetz ------------------------------
void load_nahwaermenetz()
{
        Table nahwaermenetz = loadTable("data/nahwaermenetz.csv", "header");
        for (TableRow row: nahwaermenetz.rows())
        {
                polygonsList.add(new Polygon());
                Polygon lastPolygon = polygonsList.get(polygonsList.size()-1);
                nahwaermeList.add(lastPolygon);
                lastPolygon.type = "nahwaermenetz";
                lastPolygon.id = row.getInt("id");//pass id
                lastPolygon.col = color(217, 9, 9);

                String[] lats = split(row.getString("lats"), ' '); // making list out of POLYGON geometry
                String[] lons = split(row.getString("lons"), ' ');

                for (int i = 0; i<lats.length-1; i++)
                {
                        String latString = split(lats[i], ".")[0]; // lats[0] = ganze zahl; lats[1] = dezimalstellen //using epsg3857 with [metres] --> use integer (pre-comma)
                        // fill String with zeros, until 7 digits long
                        for (int j = 0; j < 7-lats[0].length(); j++)
                        {
                                latString = latString + "0";
                        }

                        String lonString = split(lons[i], ".")[0];
                        for (int j = 0; j < 7-lons[0].length(); j++)
                        {
                                lonString = lonString + "0";
                        }
                        float y = convertToXY_epsg3857(lonString, latString, offscreen)[0];
                        float x = convertToXY_epsg3857(lonString, latString, offscreen)[1];
                        lastPolygon.latitudes = append(lastPolygon.latitudes, y);
                        lastPolygon.longitudes = append(lastPolygon.longitudes, x);

                }
        } // end iterate polygons

        println(nahwaermenetz.getRowCount() + " polygons for nahwaermenetz added.");

        for (Polygon nwn : nahwaermeList)
        {
                println("Nahwärmenetz " + nwn.id);
                for (int i = 0; i<nwn.longitudes.length; i++)
                {
                        println(nwn.longitudes[i] + "\t " + nwn.latitudes[i]);
                }
                println("----------------");
        }

        // -------------------------- global nwn for movement of FX
        // add all nahwaermenetze to global nahwaermenetz
        for (Polygon nwn : nahwaermeList)
        {
                for (int i = 0; i < nwn.longitudes.length; i++)
                {
                        nahwaermeMesh.add(new Node (nwn.longitudes[i], nwn.latitudes[i], str(nwn.id) + str(i)));
                }
        }

        // set neighbours (hard coded)
        // neighbours are marked by their IDs and separated by spaces
        // first is node to connect, following are neighbours
        String newNeighbourstring =
                "51 70 71 110 end" +
                "72 71 end" +
                "71 72 70 51 end"+
                "70 71 110 end" +
                "110 111 05 50 51 end" +
                "111 112 110 61 end" +
                "61 60 111 112 end" +
                "60 61 11 13 end" +
                "11 10 60 end" +
                "10 02 03 01 11 end" +
                "03 04 02 10 30 end" +
                "04 30 31 03 20 end" +
                "30 31 04 03 20 end" +
                "31 30 04 end" +
                "20 05 50 04 30 21 end" +
                "21 20 22 end" +
                "22 21 23 end" +
                "23 24 22 end" +
                "24 23 end" +
                "05 110 20 50 end" +
                "50 110 20 05 end" +
                "01 00 40 02 10 end" +
                "00 40 41 80 01 90 end" +
                "40 00 41 80 01 90 end" +
                "41 80 81 42 00 40 end" +
                "80 41 81 42 00 40 end" +
                "42 41 80 43 end" +
                "43 42 end" +
                "80 41 42 00 40 81 end" +
                "81 41 80 82 end" +
                "82 81 83 end" +
                "83 82 84 end" +
                "84 83 end" +
                "90 00 40 91 end" +
                "91 90 100 end" +
                "92 100 end" +
                "100 101 92 91 end" +
                "101 100 end"
        ;

        setMeshNeighbours(newNeighbourstring);

        // define globalGoal
        for (Node node : nahwaermeMesh)
        {
                if (node.str_id.equals("90"))
                {
                        globalGoal = node;
                        break;
                }
        }

//  polygonsList.get(polygonsList.size() - 4).col = superColor; // for demonstration only
}


// ----------------------------------- basemap ---------------------------------
void load_basemap(String map)
{
        basemap = loadImage(map);
        /* extent:
           lower left: 1012695.0710094821406528,7205976.7903914991766214
           upper right:1014205.5283626030432060,7207571.7344451360404491
         */
        int imgLonMax = 1014205;
        int imgLatMax = 7207571;
        int imgLonMin = 1012695;
        int imgLatMin = 7205976;
        int imgLonDiff = imgLonMax - imgLonMin;
        int imgLatDiff = imgLatMax - imgLatMin;

        if (rotationDegrees == 0)
        {
                // img_delta_X = int(imgLonDiff * offscreen.width / float(lonDiff));
                // img_delta_Y = int(img_delta_X * basemap.height / float(basemap.width));
                img_delta_Y = int(imgLatDiff * offscreen.height) / area.latDiff;
                img_delta_X = int(imgLonDiff * offscreen.width) / area.latDiff;
                imgOffsetY = int((area.latMax - imgLatMax) / (float(area.latDiff) / offscreen.height));
                imgOffsetX = ((imgLonMin - area.lonMin) * offscreen.width) / area.latDiff;
        }

        else if (rotationDegrees == 90)
        {
                img_delta_Y = int(imgLatDiff * (area.resoX * offscreen.width/float(area.lonDiff))); // Δy soll (verhältnismäßig) mit Canvas-BREITE gleichgesetzt werden
                img_delta_X = int(img_delta_Y * (basemap.width/float(basemap.height)));

                println("img_delta_X = " + img_delta_X + ", img_delta_Y = " + img_delta_Y);
                imgOffsetY = int((area.latMax - imgLatMax) * (offscreen.width/float(area.latDiff)));
                imgOffsetX = int((imgLonMin - area.lonMin) * (offscreen.height/float(area.lonDiff)));

                println("imgOffsetX = " + imgOffsetX + ", imgOffsetY = " + imgOffsetY);
        }
}
}
