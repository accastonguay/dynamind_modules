__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
import math


class education(Module):
        display_name = "Education campaign"
        group_name = "Decisions"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("education", DOUBLE)
            self.education = 1


            self.city = ViewContainer("city", COMPONENT, READ)
            self.city.addAttribute("dam_volume", Attribute.DOUBLE, READ)
            self.city.addAttribute("education", Attribute.DOUBLE, WRITE)



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


                def bass(N,p,q,t):
                    result = N*((1-math.exp(-(p+q)*t))/(1+(q/p)*math.exp(-(p+q)*t)))
                    return result
                # edu = 1+(200+-bass(200,0.000025,0.01,volume))/100
                edu = 1+(100+-bass(100,0.000025,0.01,volume))/100

                b.SetField("education", edu)



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
