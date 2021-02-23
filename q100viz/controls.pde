
int globalVerboseLevel = 1; // verbose level of console prints
static int maxVerboseLevel = 5;

void println_log(String message, int verboseLevel)
{
        if (globalVerboseLevel >= verboseLevel) println(message);
}

void print_log(String message, int verboseLevel)
{
        if (globalVerboseLevel >= verboseLevel) print(message);
}

void printArray_log(float[] input_array, int verboseLevel)
{
        if (globalVerboseLevel >= verboseLevel) printArray(input_array);
}

void keyPressed() {
        if (key == CODED) // TODO: fix this.. it rotates weirdly (no translation implemented? recast the x-y-resolution?)
        {
                if (keyCode == UP) rotationDegrees = 0;
                if (keyCode == LEFT) rotationDegrees = 90;
                if (keyCode == DOWN) rotationDegrees = 180;
                if (keyCode == RIGHT) rotationDegrees = 270;

        }


        switch(key) {
        case ' ':
                displayHeatFlowFX = !displayHeatFlowFX;
                break;

        case 'g':
                // toggle help text
                grid.display = !grid.display;
                break;

        case 'h':
                // toggle help text
                helpText = !helpText;
                if (!helpText) checkbox.hide();
                if (helpText) checkbox.show();
                break;

        case 'c':
                // enter/leave calibration mode, where surfaces can be warped
                // and moved
                ks.toggleCalibration();
                break;

        case 'l':
                // loads the saved layout
                String keystone_file = "keystone_rot" + str(rotationDegrees) + ".xml";
                ks.load(keystone_file);
                break;

        case 'm':
                showBaseMap = !showBaseMap;
                break;


        case 'p':
                // toggle polygons
                displayPolygons = !displayPolygons;
                break;

        case 'r':
                for (Building building : buildingsList)
                {
                        building.co2 = random(1);
                }

                for (Building building : buildingsList)
                {
                        building.assignColor();
                }
                break;

        case 's':
                // saves the layout
                String keystone_file_export = "keystone_rot" + str(rotationDegrees) + ".xml";
                ks.save(keystone_file_export);
                break;

        case 't':
                for (Polygon zone : gis.typologiezonenList)
                {
                        zone.visible = !zone.visible;
                }
                break;

        case 'v':
                globalVerboseLevel = (globalVerboseLevel + 1) % maxVerboseLevel;
                println("global verbose level = " + globalVerboseLevel);
                break;

        case 'V':
                globalVerboseLevel = max(0, globalVerboseLevel - 1);
                println("global verbose level = " + globalVerboseLevel);
                break;



        // ----------------------------- Select ID
        case '0':
                selectedID = 0;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '1':
                selectedID = 1;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '2':
                selectedID = 2;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '3':
                selectedID = 3;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '4':
                selectedID = 4;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '5':
                selectedID = 5;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '6':
                selectedID = 6;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '7':
                selectedID = 7;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '8':
                selectedID = 8;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '9':
                selectedID = 9;
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        case '+':
                selectedID = (selectedID + 1) % 12;
                println_log("selected ID = " + selectedID, 1);
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;

        case '-':
                selectedID--;
                selectedID = (selectedID < 0) ? 11 : selectedID;
                println_log("selected ID = " + selectedID, 1);
                selectBuildingsInTypo(selectedID);
                statsViz.sendCommand(stats, 6155);
                break;
        }
}

void mousePressed() {

        // toggle building connection upon click
        for (Building building : buildingsList)
        {
                if (polygon_contains_pixel(building.polygon, surfaceMouse))
                {
                        building.connected = !building.connected;
                        building.assignColor();
                        building.co2 = 0;
                        println_log("selected building [" + building.id + "] connection = " + building.connected, 2);
                }
        }
}

void mouseDragged() {
        //sandbox.clickPiece(selectedID, surfaceMouse.x, surfaceMouse.y);
}

//------------------- start CO2-timeseries upon checkbox click -----------------
void controlEvent(ControlEvent theEvent) {
        if (theEvent.isFrom(checkbox)) {
                timeSeries.running = !timeSeries.running;
                timeSeries.loadCO2series("data/fiktive_CO2_daten.csv");
                // myColorBackground = 0;
                // print("got an event from "+checkbox.getName()+"\t\n");
                // checkbox uses arrayValue to store the state of
                // individual checkbox-items. usage:
                // println(checkbox.getArrayValue());
                // int col = 0;
                // for (int i=0;i<checkbox.getArrayValue().length;i++) {
                //   int n = (int)checkbox.getArrayValue()[i];
                //   print(n);
                //   if(n==1) {
                //     myColorBackground += checkbox.getItem(i).internalValue();
                //   }
                // }
                // println();
        }
}
