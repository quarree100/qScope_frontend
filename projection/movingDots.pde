////////////////////////////////////////////////////////////////////////////////
///////////////////////////// PATHFINDING NETWORK //////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//---------------------------Nodes for pathfinding------------------------------

Node globalGoal = null;

class Node
{
int xPos, yPos;
ArrayList<Node> neighbours = new ArrayList<Node>();
ArrayList<Node> path = new ArrayList<Node>();
String str_id;
float f = 0; // f is the total cost of the Node
float h = 0; // estimated distance to globalGoal (heat pump)
float g = 0; // distance between current and start node
Node predecessor; // needed for pathFinding

Node(float xin, float yin, String idin)
{
        xPos = int(xin);
        yPos = int(yin);
        str_id = idin;
        PVector hfrom = new PVector(xPos, yPos);
        PVector hto = new PVector(polygonsList.get(193).longitudes[0],  polygonsList.get(193).latitudes[0]); // TODO: access waermezentrale by polygon-specific id!
        h = hfrom.dist(hto);
        println_log(("Node #" + str_id + " " + xPos + "|" + yPos + " h" + h + " created"), 2);
}

void render(PGraphics p)
{
        for (Node neighbour : neighbours)
        {
                p.strokeWeight(1);
                p.stroke(255);
                p.line(xPos, yPos, neighbour.xPos, neighbour.yPos);
        }

        if (globalVerboseLevel >= 3)
        {
                p.strokeWeight(3);
                p.stroke(193, 254, 224);
                for (int i = 1; i<path.size(); i++)
                {
                        p.line(path.get(i-1).xPos, path.get(i-1).yPos, path.get(i).xPos, path.get(i).yPos);
                }
                p.noStroke();
        }
}

void setNeighbours(ArrayList<Node> nin)
{
        neighbours = nin;
        print_log("neighbouring " + this.str_id, 2);
        for (Node neighbour : neighbours)
        {
                print_log("--" + neighbour.str_id, 2);
        }
        println_log("", 2);
}

void resetVals()
{
        f = 0; // f is the total cost of the Node
        g = 0; // distance between current and start node
        PVector hfrom = new PVector(xPos, yPos);
        PVector hto = new PVector(polygonsList.get(193).longitudes[0],  polygonsList.get(193).latitudes[0]);// TODO: access waermezentrale by polygon-specific id!
        h = hfrom.dist(hto);
}

} // Node class end

//------------------ setup functions for pathfinding ---------------------------
void setMeshNeighbours(String newNeighbourstring_in)
{
        String[] splitString = newNeighbourstring_in.split("end");
        for (String subSplit : splitString)
        {
                splitString = subSplit.split(" ");

                for (Node node : GIS_Data.nahwaermeMesh)
                {
                        boolean foundAny = false;
                        ArrayList<Node> newNeighbours = new ArrayList<Node>();
                        if (node.str_id.equals(splitString[0])) // first part is always starting node
                        {
                                for (int i = 1; i<splitString.length; i++)
                                {
                                        for (Node otherNode : GIS_Data.nahwaermeMesh)
                                        {
                                                if (otherNode.str_id.equals(splitString[i])) newNeighbours.add(otherNode);
                                                foundAny = true;
                                        }
                                }
                        }
                        if (foundAny) node.setNeighbours(newNeighbours);
                }
        }
}

// ------------------- "A* path finding" algorithm: ----------------------------

ArrayList<Node> findPath(Node startNode, Node globalGoal)
{
        // initialize priorityQueue openList (priority according to f-value)
        // f-value is probability route length
        ArrayList<Node> openList = new ArrayList<Node>();
        ArrayList<Node> closedList = new ArrayList<Node>();
        openList.add(startNode);

        println_log("--------- path finding for node " + startNode.str_id, 3);

        do // runs until optimal solution found
        {
                double lowestF = Double.POSITIVE_INFINITY;
                Node lowestFNode = null;

                // find lowest f node on openList
                for (Node openNode : openList)
                {
                        if (openNode.f < lowestF)
                        {
                                lowestF = openNode.f;
                                lowestFNode = openNode;
                        }
                }
                Node currentNode = lowestFNode; // remove node with lowest f-value
                openList.remove(currentNode);
                println_log(currentNode.str_id + "removed from openList", 3);

                // add current node to closed list so it will not be used anymore
                closedList.add(currentNode);
                println_log(currentNode.str_id + "added to closedList", 3);

                // goal found?
                if (currentNode == globalGoal)
                {
                        // return totalPath;
                        ArrayList<Node> totalPath = new ArrayList<Node>();
                        Node iterNode = globalGoal;
                        print_log("path found!", 3);
                        do
                        {
                                totalPath.add(iterNode);
                                print_log("--" + iterNode.str_id, 3);
                                iterNode = iterNode.predecessor;
                        } while (iterNode != null);
                        println_log("\n", 3);

                        // reset vals for next pathFinding
                        for (Node temp_node: GIS_Data.nahwaermeMesh)
                        {
                                temp_node.resetVals();
                        }

                        return totalPath;
                }

                // generate children
                // if goal not found yet: put all neighbours onto openList
                print_log("\ngenerating children from neighbours:", 3);

                for (Node neighbour : currentNode.neighbours)
                {
                        print_log(" " + neighbour.str_id, 3);
                        if (closedList.contains(neighbour))
                        {
                                print_log(" (closed)", 3);
                                continue;
                        }

                        // update f and g
                        PVector currentNodePos = new PVector(currentNode.xPos, currentNode.yPos);
                        PVector neighbourPos = new PVector(neighbour.xPos, neighbour.yPos);
                        neighbour.g = currentNode.g + currentNodePos.dist(neighbourPos);
                        neighbour.f = neighbour.g + neighbour.h;

                        // neighbour already on openList:
                        if (openList.contains(neighbour))
                        {
                                print_log("(open)", 3);
                                for (Node open_node : openList)
                                {
                                        if (neighbour.g > open_node.g)
                                        {
                                                continue;
                                        }
                                }
                        }
                        openList.add(neighbour);
                        print_log(", added to openList", 3);
                        neighbour.predecessor = currentNode;

                } // end iterate neighbour

                print_log("\nclosedList =", 3);
                for (Node closedNode : closedList)
                {
                        print_log(" " + closedNode.str_id, 3);
                }
                println_log("", 3);
                print_log("openList =", 3);
                for (Node openNode : openList)
                {
                        print_log(" " + openNode.str_id, 3);
                }
                println_log("", 3);

        } while (openList.size() > 0);
        println_log("findPath(): no path found", 3);
        return null;
}


////////////////////////////////////////////////////////////////////////////////
/////////////////////////// MOVING DOTS FX CLASS ///////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// path finding algorithm adapted from
// https://www.openprocessing.org/sketch/413945 by Yuri Konoplev
// the original code at https://forum.processing.org/two/discussion/15700/orthogonal-projection-of-a-point-onto-a-line by cameyo

ArrayList<FX> movingPointsList = new ArrayList<FX>();

class FX
{
ArrayList<PVector> targetsList = new ArrayList<PVector>(); // contains waypoints for dot to move, stored in goal-first (i.e. reversed) order
ArrayList<Node> path = new ArrayList<Node>();
float x1,y1,x2,y2; // global for visualization poruposes
PVector p1,p2; // initial values (line ends) for line to be projected onto
PVector pp1, pp2; // for auxiliary projection lines
PVector currentPos, nextStep, previousStep, proj; // steps are for polygons stored in targetsList
int targetsPointer = 1;
int targetsPointerIncrement = -1; // initially negative to iterate through targetsList reversely
int t = 0;
float increment = 0;
float cx;
float cy;

Building parentBuilding; // each dot is associated to one building. this is used to check whether building is connected or not

// initiate new Object with x and y position:
FX(float inx, float iny){
        cx = inx;
        cy = iny;
        currentPos = new PVector(inx, iny);
        pp1 = pp2 = new PVector(0,0);
        previousStep = currentPos;
}

// returns ArrayList to be stored in targetsList.
ArrayList<PVector> generatePath()
{

        float shortestDist = 999999999; // inifinty
        Node firstNode = null;

        // ----------------------------------------------------for each polygon
        for (Node waypoint : GIS_Data.nahwaermeMesh)
        {
                print_log("starting " + waypoint.str_id, 3);
                // ----------------------------- get each pair of line vertices
                // for (int i = 1; i < waypoint.neighbours.size(); i++)
                for (Node neighbour : waypoint.neighbours)
                {
                        p1 = new PVector(waypoint.xPos, waypoint.yPos);
                        p2 = new PVector(neighbour.xPos, neighbour.yPos);
                        PVector tempProj = projection(p1, p2, currentPos); // currentPos must be initial starting point!

                        // ---------------------------- create projection
                        // if (inside(p1, p2, currentPos, 10))
                        if (inside(p1, p2, currentPos, 50)) // TODO: certain tolerance needed, otherwise projection seems to fail! but this way, dots may float towards empty location..
                        {
                                if (currentPos.dist(tempProj) < shortestDist)
                                {
                                        // ------------------ evaluate distance
                                        shortestDist = currentPos.dist(tempProj);
                                        firstNode = new Node(tempProj.x, tempProj.y, waypoint.str_id + neighbour.str_id); // first node has id of p1+p2
                                        GIS_Data.nahwaermeMesh.add(firstNode);
                                        println_log("found possible projection. new node with id " + firstNode.str_id + " created.", 3);
                                        setMeshNeighbours(firstNode.str_id + " " + waypoint.str_id + " " + neighbour.str_id + " end");
                                        nextStep = tempProj;
                                        pp1 = p1; // Hilfslinien für Vektorprojektion
                                        pp2 = p2;
                                        path = findPath(firstNode, globalGoal);

                                        ArrayList<PVector> generatedTargetsList = new ArrayList<PVector>();

                                        // convert node to vector; add to targetsList
                                        for (Node n_to_vec : path)
                                        {
                                                PVector n_vec = new PVector(n_to_vec.xPos, n_to_vec.yPos);
                                                generatedTargetsList.add(n_vec);
                                                // println_log("last added vector: " + n_vec, 4);
                                        }
                                        generatedTargetsList.add(previousStep);
                                        generatedTargetsList.add(nextStep);
                                        // generatedTargetsList.add(currentPos);
                                        targetsPointer = generatedTargetsList.size() - 1;
                                        return generatedTargetsList;
                                }
                        } // inside end
                        else if (currentPos.dist(p1) < shortestDist || currentPos.dist(p2) < shortestDist) // else go to closest vertex point
                        {
                                if (currentPos.dist(p1) < currentPos.dist(p2))
                                {
                                        shortestDist = currentPos.dist(p1);
                                        firstNode = waypoint;
                                }
                                else
                                {
                                        shortestDist = currentPos.dist(p2);
                                        firstNode = neighbour;
                                }
                                print_log("... no projection found. distance is = " + shortestDist, 3);

                                nextStep = (currentPos.dist(p1) < currentPos.dist(p2)) ? p1 : p2;
                                pp1 = p1;
                                pp2 = p2;
                        }

                } // end iterate waypoint's neighbours
                println_log(" ... ready.", 3);
        } // end iterate waypoints
        println_log("generatePath(): no path found.", 3);
        return null;
}

// with line_p1 and line_p2 as the line ends and p as the orthogonal vector
PVector projection(PVector line_p1, PVector line_p2, PVector pvec){

        float y1 = line_p1.y;
        float y2 = line_p2.y;
        float x1 = line_p1.x;
        float x2 = line_p2.x;

        if ((x1 == x2) && (y1 == y2))
                return line_p1;

        float k = ((y2-y1) * (cx-x1) - (x2-x1) * (cy-y1)) / (sq(y2-y1) + sq(x2-x1));
        float x4 = pvec.x - k * (y2-y1);
        float y4 = pvec.y + k * (x2-x1);

        return new PVector(x4,y4);
}

// projection inside line?
boolean inside(PVector line_p1, PVector line_p2, PVector proj, float tolerance){
        boolean x_res = false;
        boolean y_res = false;
        if ((tolerance + line_p1.x >= proj.x) && (proj.x >= line_p2.x - tolerance)) {
                x_res = true;
        }

        if ((line_p1.x - tolerance <= proj.x) && (proj.x <= line_p2.x + tolerance)) {
                x_res = true;
        }

        if ((line_p1.y + tolerance >= proj.y) && (proj.y >= line_p2.y - tolerance)) {
                y_res = true;
        }

        if ((line_p1.y - tolerance <= proj.y) && (proj.y <= line_p2.y + tolerance)) {
                y_res = true;
        }

        return (x_res && y_res);
}


void render(PGraphics p)
{
        p.pushStyle();

        // projection help
        if (globalVerboseLevel >= 2)
        {
                p.noStroke();
                p.fill(220,20,20);
                p.ellipse(cx,cy,8,8); // red dots indicating globalStart

                p.fill(52, 185, 194);
                p.ellipse(pp1.x, pp1.y, 10, 10); // outer points
                p.ellipse(pp2.x, pp2.y, 10, 10);
                p.strokeWeight(3);
                p.stroke(107, 225, 233);
                p.line(pp1.x, pp1.y, pp2.x, pp2.y); // projection base line

                if (globalVerboseLevel >= 3)
                {
                        p.stroke(255);
                        p.line(cx, cy, nextStep.x, nextStep.y); // Hilfslinie from-to
                }
        }

        // draw dot at current position:
        p.stroke(246, 219, 139);
        p.fill(246, 219, 139);
        p.ellipse(currentPos.x, currentPos.y, 5, 5);

        p.stroke(220);
        moveInterval(previousStep, nextStep);

        p.popStyle();
}

//increases step to move towards target
void moveInterval(PVector tempStart, PVector tempGoal)
{
        if(currentPos.dist(tempGoal) > 1) // 1 is threshold value for distance
        {
                currentPos = PVector.sub(tempGoal,tempStart);
                currentPos.mult(increment);
                currentPos.add(tempStart);
        }
        else if (currentPos.dist(tempGoal) < 1) // target reached
        {
                increment = 0;
                t = 1;
                currentPos.set(tempStart);
                tempStart.set(targetsList.get(targetsPointer)); // make next start last goal
                targetsPointer += targetsPointerIncrement;
                if (targetsPointer < 1 || targetsPointer == targetsList.size() - 1)
                {
                        targetsPointerIncrement = targetsPointerIncrement * (-1); // change direction to walk
                }
                tempGoal.set(targetsList.get(targetsPointer));
        }

        // linear movement normalized to vector length
        PVector v = PVector.sub(tempGoal, tempStart);
        t++;
        increment = (v.mag() > 0) ? t / v.mag() : 0.1;
}
} // class FX end

void initialFXpathFinding() // creates FX dots for movingPointsList and generates paths
{
        // initial path finding for FX
        for (Building building : buildingsList)
        {
                // create FX dots and generate paths
                movingPointsList.add(new FX(building.polygon.longitudes[0], building.polygon.latitudes[0]));
                movingPointsList.get(movingPointsList.size() - 1).parentBuilding = building;
                if (movingPointsList.get(movingPointsList.size() - 1).generatePath() != null)
                {
                        movingPointsList.get(movingPointsList.size() - 1).targetsList = movingPointsList.get(movingPointsList.size() - 1).generatePath();
                } else
                {
                        movingPointsList.remove(movingPointsList.size() - 1);
                }
        }
        println("heatflow FX created and pathfinding applied.");
}
