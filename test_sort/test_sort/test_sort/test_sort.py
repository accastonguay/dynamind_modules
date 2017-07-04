__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *
import numpy as np


class test_sort(Module):
        display_name = "test_sort"
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
            self.wsuds = ViewContainer("wsuds", COMPONENT, READ)

            self.wsuds.addAttribute("year_const", Attribute.INT, READ)


            #Compile views
            views = []
            views.append(self.wsuds)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            self.wsuds.reset_reading()
            # self.city.reset_reading()
            '''Price dictionaries for three categories of uses if year = y+1 for y-y+1 period '''

            for b in self.wsuds:
                year = b.GetFieldAsInteger("year_const")
                print 'Construction year = '+str(year)

            self.wsuds.finalise()
