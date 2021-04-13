/**
 * This sketch is written for the use with a CityScope table for the research in sociotechnical partizipation processes in the QUARREE100 project at the Department for Resilient Energy Systems, Bremen University.
 *
 * by David Unland
 * unland@uni-bremen.de
 *
 * March-2021
 *
 * based on the RoadMapSandbox Code by Ira Winder, ira@mit.edu
 *
 */
 String NAME = "dunland";
 String TITLE = "CityScope_QUARREE100";
 String INSTITUTE = "Bremen University";

 //------------------------------- input data ----------------------------------
 String BUILDINGS_FILE = "data/buildings.csv";
 String WAERMEZENTRALE_FILE = "data/waerme_zentrale.csv";
 String TYPOLOGIEZONEN_FILE = "data/typoTable.csv";
 String NAHWAERMENETZ_FILE = "data/nahwaermenetz.csv";
 String BASEMAP_FILE = "180111-QUARREE100-RK_modifiziert_flippedY_smaller.tga";

//-------------------------------- keystone ------------------------------------
import deadpixel.keystone.*;
Keystone ks;
CornerPinSurface surface;
PGraphics offscreen;
PVector surfaceMouse;

// declare grid:
Grid grid;

//----------------------------- GUI controls -----------------------------------
import controlP5.*;
ControlP5 cp5;
CheckBox checkbox;

// global controls:
boolean showBaseMap = true; // shows basemap from the beginning (or not). can be toggled with key 'm'
boolean showSurfaceMouse = true;
boolean displayHeatFlowFX = false;
boolean displayPolygons = true; // displays shapefiles (or not)
int rotationDegrees = 90; // variable to rotate projection by -- change with arrow keys

boolean helpText = true;
boolean gridLines = true;

GIS gis;
StatsViz statsViz;
TimeSeries timeSeries;

////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// SETUP ////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

void setup() {

        // frameRate(5);
        grid = new Grid(11);
        gis = new GIS(1013102, 1013936, 7206177, 7207365); // new GIS layer with geographic area boundaries

        // size(1280, 1024, P3D);
        size(1920, 1080, P3D); // Use this size for your projector

        // ----------------------------- controls ------------------------------
        // checkbox for starting the CO2_Series-Simulation
        cp5 = new ControlP5(this);
        checkbox = cp5.addCheckBox("CO2_series_checkbox")
                   .setPosition(width-120, height/3)
                   .setSize(20, 20)
                   // .setItemsPerRow(1)
                   // .setSpacingColumn(30)
                   // .setSpacingRow(20)
                   .addItem("run CO2-series demo", 1)
        ;

        // ----------------------------- KEYSTONE ------------------------------
        /* Keystone will only work with P3D or OPENGL renderers, since it relies on texture mapping to deform. We need an offscreen buffer to draw the surface we want projected. Note that we're matching the resolution of the CornerPinSurface. (The offscreen buffer can be P2D or P3D)
         */
        ks = new Keystone(this);

        if (rotationDegrees == 0)
        {
                int keystone_width = int(width * gis.area.resoX);
                surface = ks.createCornerPinSurface(keystone_width, height, 20);
                offscreen = createGraphics(keystone_width, height, P2D);
        }
        else if (rotationDegrees == 90)
        {
                int keystone_height = int(width * gis.area.resoX);
                surface = ks.createCornerPinSurface(width, keystone_height, 20); // width, height, resolution
                offscreen = createGraphics(width, keystone_height, P2D);
        }

        // Load the previously saved projection-map calibration
        String keystone_file = "keystone_rot" + str(rotationDegrees) + ".xml";
        try {
                ks.load(keystone_file);
        }
        catch (Exception e) {
                println(keystone_file + " could not be loaded.");
                ks.save();
                ks.load();
        }

        // ----------------------------- UDP -----------------------------------
        initUDP(5000, "127.0.0.1"); // create new UDP and start listening

        // -------------------------- GIS SETUP --------------------------------

        // load GIS shapefiles and create polygon objects:
        gis.load_buildings(BUILDINGS_FILE);
        gis.load_typologiezonen(TYPOLOGIEZONEN_FILE);
        gis.load_nahwaermenetz(NAHWAERMENETZ_FILE);
        gis.load_waermezentrale(WAERMEZENTRALE_FILE);

        gis.load_basemap(BASEMAP_FILE, 1014205, 7207571, 1012695, 7205976); // loads data into "basemap" image

        //  GIS objects and polygons meta data:
        selectBuildingsInTypo(selectedID);

        // send initial communication string for statsViz
        statsViz = new StatsViz();
        statsViz.evaluateMaxValues(); // has to be called after loading shapes to get max data for further processing

        // ----------------------------- TUI Grid ------------------------------
        grid.init(); // makes XY coordinates from TUI grid

        // -------------------------- COLORS and FX ----------------------------
        // random CO2 allocation:
        for (Building building : buildingsList)
        {
                building.co2 = random(1);
        }

        println_log("reso = " + gis.area.resoX, 1);

        // initial building coloring:
        color green = color(96, 205, 21);
        color red = color(213, 50, 21);

        for (Building building : buildingsList)
        {
                building.col = lerpColor(green, red, building.co2);
        }

        // Time Series:
        timeSeries = new TimeSeries("generic", 0.02);

        // load FX:
        initialFXpathFinding();
}

////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////// MAIN LOOP //////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

long last_JSON_sent = 0;
void draw() {

        // background(120,200,150);
        background(0);

        grid.check_incoming_message();

        if (millis() > last_JSON_sent + 500)
        grid.composeJSON();

        // color according to rotation
        for (int i = 0; i<tilesList.size(); i++)
        // associates color of typologiezone with rotation of grid 1:1
        {
                gis.typologiezonenList.get(i).col = color(int(tilesList.get(i).rotation), 255-int(tilesList.get(i).rotation), int(tilesList.get(i).rotation) / 2, 75);
        }
        ////////////////////////////////////////////////////////////////////////
        //////////////////////////// OFFSCREEN DRAWING /////////////////////////
        offscreen.beginDraw();

        // rotate whole image:
        // offscreen.pushMatrix();
        // offscreen.translate(offscreen.width, 0); // TODO: convert lats+longs rather than transform to make surfaceMouse hit the right buildings!
        // offscreen.rotate(radians(rotationDegrees));

        offscreen.background(0);
        // ---------------------- GIS shapes and objects -----------------------
        // draw basemap
        if (showBaseMap)
        {
                if (rotationDegrees != 0)
                {
                        offscreen.pushMatrix();
                        offscreen.translate(offscreen.width, 0);
                        offscreen.rotate(radians(rotationDegrees));
                        offscreen.image(basemap, imgOffsetX, imgOffsetY, img_delta_X, img_delta_Y);
                        offscreen.popMatrix();
                }
                else
                        offscreen.image(basemap, imgOffsetX, imgOffsetY, img_delta_X, img_delta_Y);

        }

        grid.select_polygons_via_TUI(); // marks polygons if selected via LEGO grid // TODO: only execute if new incoming message != lastMessage

        if (displayPolygons)
        {
                // Buildings
                for (Building building : buildingsList) {
                        building.render(offscreen);
                }
                // Polygons
                for (Polygon polygon : polygonsList)
                {
                        polygon.render(offscreen);
                }
        }

        // ------------------------- auxiliary info ----------------------------
        // nahwaermentz mesh
        if (globalVerboseLevel >= 2)
        {
                for (Node node : gis.nahwaermeMesh)
                {
                        node.render(offscreen);
                }
        }

        // TUI physical table grid:
        if (grid.display)
        {
                // TUI physical LEGO positions:
                grid.draw_TUI_grid(offscreen);
                grid.drawFieldEntries(offscreen);
        }


        // ------------------------------- FX ----------------------------------
        if (displayHeatFlowFX)
        {
                for (FX movingPoints : movingPointsList)
                {
                        if (movingPoints.parentBuilding.connected)
                                movingPoints.render(offscreen); // draws and moves FX objects
                }
        }

        // Draw a mouse cursor
        /* Convert the mouse coordinate into surface coordinates: this will allow you to use mouse events inside the keystone surface from your screen. */
        surfaceMouse = surface.getTransformedMouse();
        if (showSurfaceMouse)
        {
                offscreen.pushStyle();
                offscreen.stroke(88,75,219);
                offscreen.fill(110, 98, 224);
                offscreen.ellipse(surfaceMouse.x, surfaceMouse.y, 5, 5);
                offscreen.popStyle();
        }

        // -------------------------- render stuff -----------------------------
        offscreen.endDraw();

        // render the scene, transformed using the corner pin surface
        surface.render(offscreen);

        ////////////////////////////////////////////////////////////////////////
        //////////////////////////// DRAWING ON CANVAS /////////////////////////
        // ---------------------- diesplay Help Text ---------------------------
        if (helpText) {
                textAlign(RIGHT, BOTTOM);
                text("Press 'h' to hide/show this text.\n" +
                     "PROJECTION MAP KEY COMMANDS:\n\n" +
                     "'c' \t ‒ \t turn on calibration mode.\n" +
                     "'s' \t ‒ \t save calibration.\n" +
                     "'l' \t ‒ \t load calibration.\n\n" +
                     "  Use mouse to adjust.\n\n\n" +
                     "APPLICATION KEY COMMANDS:\n\n"
                     + "'m' \t ‒ \t toggle basemap\n"
                     + "'t' \t ‒ \t toggle Typologiezonen\n"
                     + "'g' \t ‒ \t toggle TUI grid\n"
                     + "'0' - '9' \t ‒ \t select Typologyzone by ID\n"
                     + "'r' \t ‒ \t random CO2 configuration\n\n"
                     + "surfaceMouse: \n" + surfaceMouse.x + " | " + surfaceMouse.y + "\n"
                     + "mouse: \n" + mouseX + " | " + mouseY + "\n"
                     + "selected ID: " + selectedID + "\t (press +/-) to change\n"
                     + "'v' \t ‒ \t higher verbose detail\n"
                     + "'V' \t ‒ \t less verbose output\n"
                     + "global verbose level: " + globalVerboseLevel + " \t(press v/V to change)\n" +
                     "\ncycle " + timeSeries.cycle
                     ,width, height-200);
        }
        textAlign(LEFT,BOTTOM);
        strokeWeight(2);

        ////////////////////////////////////////////////////////////////////////
        /////////////////////////////// TIDYING UP /////////////////////////////
        // display statistics for selected typozone in statsViz.pde:
        // TODO: only do this if statsViz is running!
        statsViz.send_stats();
        statsViz.sendInitialString();

        // ---------------------- CO2-series animation -------------------------
        if (timeSeries.running)
        {
                timeSeries.run("GAMA");
        }
}
