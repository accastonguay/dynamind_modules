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

            self.createParameter("rule", INT)
            self.rule = 1

            self.parcel = ViewContainer("parcel", COMPONENT, READ)

            self.parcel.addAttribute("year", Attribute.INT, READ)
            self.parcel.addAttribute("council", Attribute.STRING, READ)
            self.parcel.addAttribute("budget", Attribute.DOUBLE, WRITE)

            #Compile views
            views = []
            views.append(self.parcel)

            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition

        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation
            self.parcel.reset_reading()

            dict = {2005: {'MONASH': 50000, 'BAYSIDE': 0, 'PORT PHILLIP': 200000, 'STONNINGTON': 30000, 'KINGSTON': 50000,
                    'GLEN EIRA': 0},
             2006: {'MONASH': 0, 'BAYSIDE': 38000, 'PORT PHILLIP': 200000, 'STONNINGTON': 115000, 'KINGSTON': 50000,
                    'GLEN EIRA': 0},
             2007: {'MONASH': 250000, 'BAYSIDE': 0, 'PORT PHILLIP': 200000, 'STONNINGTON': 20000, 'KINGSTON': 50000,
                    'GLEN EIRA': 0},
             2008: {'MONASH': 75000, 'BAYSIDE': 0, 'PORT PHILLIP': 200000, 'STONNINGTON': 0, 'KINGSTON': 50000,
                    'GLEN EIRA': 0},
             2009: {'MONASH': 0, 'BAYSIDE': 110000, 'PORT PHILLIP': 275000, 'STONNINGTON': 105000, 'KINGSTON': 160000,
                    'GLEN EIRA': 152000},
             2010: {'MONASH': 100000, 'BAYSIDE': 0, 'PORT PHILLIP': 451000, 'STONNINGTON': 95000, 'KINGSTON': 106000,
                    'GLEN EIRA': 0},
             2011: {'MONASH': 182000, 'BAYSIDE': 0, 'PORT PHILLIP': 430000, 'STONNINGTON': 0, 'KINGSTON': 150000,
                    'GLEN EIRA': 45000},
             2012: {'MONASH': 325640, 'BAYSIDE': 0, 'PORT PHILLIP': 442000, 'STONNINGTON': 130000, 'KINGSTON': 246000,
                    'GLEN EIRA': 484000},
             2013: {'MONASH': 179000, 'BAYSIDE': 308000, 'PORT PHILLIP': 470000, 'STONNINGTON': 143000,
                    'KINGSTON': 145000, 'GLEN EIRA': 0},
             2014: {'MONASH': 355300, 'BAYSIDE': 104000, 'PORT PHILLIP': 485000, 'STONNINGTON': 120000,
                    'KINGSTON': 140000, 'GLEN EIRA': 100000}}

            for p in self.parcel:
                year = p.GetFieldAsInteger("year")
                council = p.GetFieldAsString("council")
                # print year, type(year), council, type(council)
                p.SetField("budget", dict[year][council])

            self.parcel.finalise()