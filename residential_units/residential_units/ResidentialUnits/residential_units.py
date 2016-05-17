__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *



class ResidentialUnits(Module):
        display_name = "Residential Units"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("residential_units", INT)


            self.building = ViewContainer("building", COMPONENT, READ)
            self.building.addAttribute("use_type", Attribute.STRING, READ)
            self.building.addAttribute("residential_units", Attribute.INT, WRITE)


            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.building)
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
            self.building.reset_reading()
            # self.city_environment.reset_reading()
            for b in self.building:
                use = b.GetFieldAsString("use_type")
                # restriction = b.GetFieldAsInteger("restriction")
                if use == 'Residential - R1Z' or use == 'Residential - MUZ':
                    b.SetField("residential_units", 1)
                else:
                    b.SetField("residential_units", 0)



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


            self.building.finalise()
            # self.city_environment.finalise()
