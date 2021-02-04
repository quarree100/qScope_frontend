// spiderweb diagram

void drawSpiderWebDiagram(int x, int y)
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

        v.set(cos(radians(60))*(float(heat_mean) / float(max_heat))*radius, sin(radians(60))*(float(heat_mean) / float(max_heat))*radius);
        // println(cos(radians(60)) + " " + (float(heat_mean) / float(max_heat))*radius + "\t" +  sin(radians(60)) + " " + (float(heat_mean) / float(max_heat))*radius);
        vecHeatCons.add(v);
        v.set(cos(radians(120))*(float(power_mean) / float(max_power))*radius, sin(radians(120))*(float(power_mean) / float(max_power))*radius);
        vecPowCons.add(v);
        v.set(cos(radians(180))*(float(spec_heat_mean) / 800)*radius, sin(radians(180))*(float(spec_heat_mean) / 800)*radius);
        // println(cos(radians(180)) + " " + (float(spec_heat_mean) / float(max_spec_heat)));
        vecSpecHeatCons.add(v);
        v.set(cos(radians(240))*(float(spec_power_mean_we) / float(max_spec_power_we))*radius, sin(radians(240))*(float(spec_power_mean_we) / float(max_spec_power_we))*radius);
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
