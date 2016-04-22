__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr



class Restrictions(Module):
        display_name = "Restrictions"
        group_name = "Decisions"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("restriction", INT)
            self.restriction = 0


            self.city = ViewContainer("city", COMPONENT, READ)
            self.city.addAttribute("dam_volume", Attribute.DOUBLE, READ)
            self.city.addAttribute("total_demand", Attribute.DOUBLE, READ)
            self.city.addAttribute("total_outdoor_demand", Attribute.DOUBLE, READ)
            self.city.addAttribute("restriction", Attribute.INT, WRITE)
            self.city.addAttribute("total_demand_restricted", Attribute.DOUBLE, WRITE)


            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.city)
            # views.append(self.city_environment)


            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            #print self.my_parameter

            #Data Stream Manipulation

            #print self.my_parameter
            self.city.reset_reading()
            # self.city_environment.reset_reading()
            for b in self.city:
                volume = b.GetFieldAsDouble("dam_volume")
                total_demand = b.GetFieldAsDouble("total_demand")
                total_outdoor_demand = b.GetFieldAsDouble("total_outdoor_demand")

                if volume > 980:
                    self.restriction = 0
                    b.SetField("restriction", self.restriction)
                    self.demand_restricted = total_demand
                    b.SetField("total_demand_restricted", self.demand_restricted)
                    print 'Volume is '+str(volume) +' and the restriction is 0'
                    print 'total demand is '+str(total_demand) +' and restricted use is'+str(self.demand_restricted)

                elif 980 >= volume > 800:
                    self.restriction = 1
                    b.SetField("restriction", self.restriction)
                    self.demand_restricted = total_demand - (total_outdoor_demand*0.3)
                    b.SetField("total_demand_restricted", self.demand_restricted)
                    print 'Volume is '+str(volume) +' and the restriction is 1'
                    print 'total demand is '+str(total_demand) +' and restricted use is'+str(self.demand_restricted)

                elif 800 >= volume > 600:
                    self.restriction = 2
                    b.SetField("restriction", self.restriction)
                    self.demand_restricted = total_demand - (total_outdoor_demand*0.6)
                    b.SetField("total_demand_restricted", self.demand_restricted)
                    print 'Volume is '+str(volume) +' and the restriction is 2'
                    print 'total demand is '+str(total_demand) +' and restricted use is'+str(self.demand_restricted)

                elif 600 >= volume > 400:
                    self.restriction = 3
                    b.SetField("restriction", self.restriction)
                    self.demand_restricted = total_demand - (total_outdoor_demand*0.8)
                    b.SetField("total_demand_restricted", self.demand_restricted)
                    print 'Volume is '+str(volume) +' and the restriction is 3'
                    print 'total demand is '+str(total_demand) +' and restricted use is'+str(self.demand_restricted)

                elif 400 >= volume:
                    self.restriction = 4
                    b.SetField("restriction", self.restriction)
                    self.demand_restricted = total_demand - (total_outdoor_demand*1)
                    b.SetField("total_demand_restricted", self.demand_restricted)
                    print 'Volume is '+str(volume) +' and the restriction is 4'
                    print 'total demand is '+str(total_demand) +' and restricted use is'+str(self.demand_restricted)
            self.city.finalise()




            #     self.city.restriction=0
            # elif 980000 >= self.city_environment.dam_volume > 575000:
            #     self.city.restriction=1
            # elif 575000 >= self.city_environment.dam_volume:
            #     self.city.restriction=2

            # if city_environment.GetFieldAsDouble("dam_volume") > 980000:
            #     self.city.restriction=0
            # elif 980000 >= city_environment.GetFieldAsDouble("dam_volume") > 575000:
            #     self.city.restriction=1
            # elif 575000 >= city_environment.GetFieldAsDouble("dam_volume"):
            #     self.city.restriction=2


            # for c_e in self.city_environment:
            #     d_v = c_e.GetFieldAsDouble("dam_volume")
            #     for c in self.city:
            #         r = c.GetFieldAsDouble("restriction")
            #         if d_v > 980000:
            #             self.restriction = 0
            #             c.SetField("restriction", self.restriction)
            #         elif 980000 >= d_v > 575000:
            #             self.restriction = 1
            #             c.SetField("restriction", self.restriction)
            #         elif 575000 >= d_v:
            #             self.restriction = 2
            #             c.SetField("restriction", self.restriction)

            # for c_e in self.city_environment:
            #     d_v = c_e.GetFieldAsDouble("dam_volume")
            #     print d_v
                # for c in self.city:
                #     r = c.GetFieldAsDouble("restriction")
                #     if d_v > 980000:
                #         self.restriction = 0
                #         c.SetField("restriction", self.restriction)
                #     elif 980000 >= d_v > 575000:
                #         self.restriction = 1
                #         c.SetField("restriction", self.restriction)
                #     elif 575000 >= d_v:
                #         self.restriction = 2
                #         c.SetField("restriction", self.restriction)
