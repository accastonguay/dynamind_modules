__author__ = 'acharett'

from pydynamind import *
from osgeo import ogr
from random import *

class budget(Module):
        display_name = "Council Budgets"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition
            self.__dict = {
                2005: {'MONASH': 50000, 'BAYSIDE': 0, 'PORT PHILLIP': 200000, 'STONNINGTON': 30000, 'KINGSTON': 50000,
                       'GLEN EIRA': 0},
                2006: {'MONASH': 0, 'BAYSIDE': 38000, 'PORT PHILLIP': 200000, 'STONNINGTON': 115000, 'KINGSTON': 50000,
                       'GLEN EIRA': 0},
                2007: {'MONASH': 250000, 'BAYSIDE': 0, 'PORT PHILLIP': 200000, 'STONNINGTON': 20000, 'KINGSTON': 50000,
                       'GLEN EIRA': 0},
                2008: {'MONASH': 75000, 'BAYSIDE': 0, 'PORT PHILLIP': 200000, 'STONNINGTON': 0, 'KINGSTON': 50000,
                       'GLEN EIRA': 0},
                2009: {'MONASH': 0, 'BAYSIDE': 110000, 'PORT PHILLIP': 275000, 'STONNINGTON': 105000,
                       'KINGSTON': 160000, 'GLEN EIRA': 152000},
                2010: {'MONASH': 100000, 'BAYSIDE': 0, 'PORT PHILLIP': 451000, 'STONNINGTON': 95000, 'KINGSTON': 106000,
                       'GLEN EIRA': 0},
                2011: {'MONASH': 182000, 'BAYSIDE': 0, 'PORT PHILLIP': 430000, 'STONNINGTON': 0, 'KINGSTON': 150000,
                       'GLEN EIRA': 45000},
                2012: {'MONASH': 325640, 'BAYSIDE': 0, 'PORT PHILLIP': 442000, 'STONNINGTON': 130000,
                       'KINGSTON': 246000, 'GLEN EIRA': 484000},
                2013: {'MONASH': 179000, 'BAYSIDE': 308000, 'PORT PHILLIP': 470000, 'STONNINGTON': 143000,
                       'KINGSTON': 145000, 'GLEN EIRA': 0},
                2014: {'MONASH': 355300, 'BAYSIDE': 104000, 'PORT PHILLIP': 485000, 'STONNINGTON': 120000,
                       'KINGSTON': 140000, 'GLEN EIRA': 100000}}

            self.__dict_costs = {2005: {'KINGSTON':  20000},
                                 2006: {'KINGSTON': 123000},
                                 2007: {'KINGSTON': 647684},
                                 2008: {'KINGSTON': 70000},
                                 2009: {'KINGSTON': 210000},
                                 2010: {'KINGSTON': 0},
                                 2011: {'KINGSTON': 0},
                                 2012: {'KINGSTON': 130000}}

            self.__dict_pvcosts = {2005: {'KINGSTON':  34113},
                                 2006: {'KINGSTON': 151164},
                                 2007: {'KINGSTON': 748486},
                                 2008: {'KINGSTON': 92064},
                                 2009: {'KINGSTON': 251926},
                                 2010: {'KINGSTON': 0},
                                 2011: {'KINGSTON': 0},
                                 2012: {'KINGSTON': 182791}}


            self.createParameter("source", STRING)
            self.source = "budget"

            self.createParameter("amount", DOUBLE)
            self.amount = 0

            self.council = ViewContainer("council", COMPONENT, READ)

            self.council.addAttribute("year", Attribute.INT, READ)
            self.council.addAttribute("lga_name", Attribute.STRING, READ)
            self.council.addAttribute("budget", Attribute.DOUBLE, WRITE)

            #Compile views
            views = []
            views.append(self.council)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition

        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation
            self.council.reset_reading()

            for c in self.council:
                year = c.GetFieldAsInteger("year")
                council_name = c.GetFieldAsString("lga_name")
                if self.source == "budget":
                    #print year, type(year), council, type(council)
                    c.SetField("budget", self.__dict[year][council_name])
                elif self.source == "costs":
                    c.SetField("budget", self.__dict_costs[year][council_name])
                elif self.source == "pvcosts":
                    c.SetField("budget", self.__dict_pvcosts[year][council_name])
                elif self.source == "scenario":
                    c.SetField("budget", self.amount)
                else:
                    print "***Source chosen not in choices***"

            self.council.finalise()