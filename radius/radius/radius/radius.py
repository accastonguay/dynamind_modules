__author__ = 'acharett'


from pydynamind import *
import math
from osgeo import ogr


class radius(Module):
        display_name = "Calculate radius"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.createParameter("dummy", INT)
            self.time = 1

        def init(self):
            self.wsud_points = ViewContainer("wsud_points", COMPONENT, READ)

            self.wsud_points.addAttribute("conv_area", Attribute.DOUBLE, READ)
            self.wsud_points.addAttribute("radius", Attribute.DOUBLE, WRITE)

            #Compile views
            views = []
            views.append(self.wsud_points)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            self.wsud_points.reset_reading()
            # self.city.reset_reading()
            '''Price dictionaries for three categories of uses if year = y+1 for y-y+1 period '''

            for b in self.wsud_points:
                area = b.GetFieldAsInteger("conv_area")
                r = math.sqrt(area/math.pi)
                b.SetField("radius", r)


            self.wsud_points.finalise()
