/**
 * This sketch is written for the use with a CityScope table for the research in sociotechnical partizipation processes in the QUARREE100 project at the Department for Resilient Energy Systems, Bremen University.
 *
 * THIS SKETCH MUST BE RUN IN PROCESSING 2!
 *
 * by David Unland
 * unland@uni-bremen.de
 *
 * Jan-2021
 *
 * based on the RoadMapSandbox Code by Ira Winder, ira@mit.edu
 *
 */

// GUI
import controlP5.*;

ControlP5 cp5;
CheckBox checkbox;

// These are libraries and objects needed for projection mapping (i.e. Keystone Library Objects)
// ATTENTION: MUST BE RUN IN PROCESSING 2; library not available for p3
import deadpixel.keystone.*;
Keystone ks;
CornerPinSurface surface;
PGraphics offscreen;
PVector surfaceMouse;

// import gifAnimation.*;
// GifMaker gifExport;
// boolean exportGif = false;
// int k = 0; // used for steps (frames) for gif export

// declare grid:
Grid grid;

//----------------------------- GUI controls -----------------------------------
boolean showBaseMap = true; // shows basemap from the beginning (or not). can be toggled with key 'm'
boolean showSurfaceMouse = true;
boolean displayHeatFlowFX = false;
boolean displayPolygons = true; // displays shapefiles (or not)
int rotationDegrees = 90; // variable to rotate projection by -- change with arrow keys

// -------------- coordinate reference system information ----------------------
int crs = 3857; // define coordinate reference systeme. Will be used to load table and draw shapes. so far: crs=3857
// get these coordinates from GIS map:
int lonMin = 1013102; // 1013137; //9.0975364; // y = 0
int lonMax = 1013936; // 1013901; //9.1143553; // height
int latMin = 7206177; // 7206217; //54.1876916; // x = 0
int latMax = 7207365; // 7207334; //54.1988598; // width
int lonDiff = lonMax - lonMin;
int latDiff = latMax - latMin;
float resoX = float(lonDiff)/latDiff;

GIS GIS_Data;

// basemap
PImage basemap;
int img_delta_Y; // to be declared at loadGISbasemap
int img_delta_X;
int imgOffsetY; // to be declared at loadGISbasemap
int imgOffsetX;

boolean helpText = true;
boolean gridLines = true;
String stats; // String to be sent to statsViz

////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// SETUP ////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

void setup() {

        // instantiate grid:
        grid = new Grid(22);

        // frameRate(5);

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

        // float keystone_height = width / float(width * ()(lonMax-lonMin)/float(latMax-latMin)));

        if (rotationDegrees == 0)
        {
                int keystone_width = int(width * resoX);
                surface = ks.createCornerPinSurface(keystone_width, height, 20);
                offscreen = createGraphics(keystone_width, height, P2D);
        }
        else if (rotationDegrees == 90)
        {
                int keystone_height = int(width * resoX);
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
        initUDP();

        // -------------------------- GIS SETUP --------------------------------

        GIS_Data = new GIS();
        // load GIS shapefiles and create polygon objects:
        GIS_Data.load_buildings();
        GIS_Data.load_typologiezonen();
        GIS_Data.load_nahwaermenetz();
        GIS_Data.load_waermezentrale();

        GIS_Data.load_basemap("180111-QUARREE100-RK_modifiziert_flippedY_smaller.tga"); // loads data into "basemap" image

        //  GIS objects and polygons meta data:
        selectBuildingsInTypo(selectedID);
        evaluateMaxValues(); // has to be called after loading shapes to get max data for further processing

        // send initial communication string for statsViz
        String initComm = ("init values" + "\n" + max_heat + "\n" + max_power + "\n" + max_spec_heat + "\n" + max_spec_power_we + "\n" + max_spec_power_m2 + "\n" + min_heat + "\n" + min_power + "\n" + min_spec_heat + "\n" + min_spec_power_we + "\n" + min_spec_power_m2);
        sendCommand(initComm, 6155); // sends min and max values to statsViz.pde

        // ----------------------------- TUI Grid ------------------------------
        grid.init(); // makes XY coordinates from TUI grid

        // -------------------------- COLORS and FX ----------------------------
        // random CO2 allocation:
        for (Building building : buildingsList)
        {
                building.co2 = random(1);
        }

        println_log("reso = " + resoX, 1);

        // initial building coloring:
        color green = color(96, 205, 21);
        color red = color(213, 50, 21);

        for (Building building : buildingsList)
        {
                building.col = lerpColor(green, red, building.co2);
        }

        // load FX:
        initialFXpathFinding();
}

////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////// MAIN LOOP //////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

void draw() {

        background(120,200,150);

        grid.check_incoming_message();

        // color according to rotation
        for (int i = 0; i<tilesList.size(); i++)
        // associates color of typologiezone with rotation of grid 1:1
        {
                GIS_Data.typologiezonenList.get(i).col = color(int(tilesList.get(i).rotation), 255-int(tilesList.get(i).rotation), int(tilesList.get(i).rotation) / 2, 75);
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
                for (Node node : GIS_Data.nahwaermeMesh)
                {
                        node.render(offscreen);
                }
        }

        // TUI physical table grid:
        // int gridScale_ = offscreen.height/squareFields;
        // int shorterDimension = (offscreen.height < offscreen.width) ? offscreen.height : offscreen.width;         // makes this rotation-dependent
        if (grid.display)
        {
                // for (int i = 0; i<shorterDimension; i+=gridScale_)
                // {
                //         offscreen.strokeWeight(1);
                //         offscreen.stroke(120);
                //         offscreen.line(i, 0, i, shorterDimension - 0.5*gridScale_);
                //         offscreen.line(0, i, shorterDimension - gridScale_*0.5, i);
                // }
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
                     "Projection Map Key Commands:\n\n" +
                     "'c' \t ‒ \t turn on calibration mode.\n" +
                     "'s' \t ‒ \t save calibration.\n" +
                     "'l' \t ‒ \t load calibration.\n\n" +
                     "  Use mouse to adjust.\n\n\n" +
                     "Application Key Commands:\n\n"
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
                     + "global verbose level: " + globalVerboseLevel + " \t(press v/V to change)\n"
                     ,width, height-200);
        }

        ////////////////////////////////////////////////////////////////////////
        /////////////////////////////// TIDYING UP /////////////////////////////
        // display statistics for selected typozone in statsViz.pde:
        composeStatsToSend();
        sendCommand(stats, 6155);

        String initComm = ("init" + "\n" + max_heat + "\n" + max_power + "\n" + max_spec_heat + "\n" + max_spec_power_we + "\n" + max_spec_power_m2 + "\n" + min_heat + "\n" + min_power + "\n" + min_spec_heat + "\n" + min_spec_power_we + "\n" + min_spec_power_m2);
        sendCommand(initComm, 6155);

        // ---------------------- CO2-series animation -------------------------
        if (do_runCO2series)
        {
                runCO2series();
        }
}
