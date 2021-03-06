__author__ = 'acharett'

from pydynamind import *

import damage_curves

class MyModule(Module):
        display_name = "Flood damage"
        group_name = "Economic Evaluation"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("damage", DOUBLE)
            #self.damage = 5.

            self.building = ViewContainer("building", COMPONENT, READ)
            self.building.addAttribute("flood_height", Attribute.DOUBLE, READ)
            self.building.addAttribute("area", Attribute.DOUBLE, READ)
            self.building.addAttribute("use_type", STRING, READ)



            self.building.addAttribute("damage", Attribute.DOUBLE, WRITE)

            self.registerViewContainers([self.building])

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """
        def run(self):
            #Data Stream Manipulation

            #print self.my_parameter
            self.building.reset_reading()
            counter_residential = 0
            counter_commercial = 0
            damage_residential = 0
            damage_commercial = 0
            ip = 0
            rp = 0
            for b in self.building:
                h = b.GetFieldAsDouble("flood_height")
                a = b.GetFieldAsDouble("area")
                u = b.GetFieldAsString("use_type")
                f = b.GetFieldAsInteger("flood_id")
                b.SetField("damage", self.damage)

                ''' Restrict buildings to flooded area'''
                if f > 0 and type(u) == str:



                    # Damage if use_type == Residential
                    if 'Residential' in u:
                        if h > 0.5:
                            rp += 1
                        if a < 80:
                            self.damage = damage_curves.res_direct_small(h)
                            counter_residential += 1
                            damage_residential += self.damage
                        elif 80 <= a <= 140:
                            self.damage = damage_curves.res_direct_medium(h)
                            counter_residential += 1
                            damage_residential += self.damage

                        elif 140 < a :
                            self.damage = damage_curves.res_direct_large(h)
                            counter_residential += 1
                            damage_residential += self.damage


                    # Damage if use_type == Commercial
                    elif 'Business' or 'Industrial' in u:
                        self.damage = damage_curves.comm_direct(h)*a + damage_curves.comm_indirect(h)*a
                        counter_commercial += 1
                        damage_commercial += self.damage


                    if h > 0.5:
                        ip += 1


            damage_vehicles = damage_curves.vehicles(rp, ip)

                #Clean-up cost
            print 'Total number of residences flooded is ' + str(counter_residential)
            print 'Total number of commercial or industrial properties flooded is ' + str(counter_commercial)
            print 'Total amount of residential damage is ' + str(damage_residential)
            print 'Total amount of commercial or industrial damage is ' + str(damage_commercial)
            print 'Total amount of damage on vehicles is ' + str(damage_vehicles)

            self.building.finalise()
