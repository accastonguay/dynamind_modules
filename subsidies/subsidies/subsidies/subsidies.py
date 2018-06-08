__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *



class subsidies(Module):
        display_name = "Subsidies"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            #
            # self.createParameter("scenario_inc2", DOUBLE)
            # self.createParameter("scenario_inc5", DOUBLE)
            # self.createParameter("scenario_inc_out", DOUBLE)
            # self.scenario_inc2 = 0
            # self.scenario_inc5 = 0
            # self.scenario_inc_out = 0

            self.city = ViewContainer("city", COMPONENT, READ)

            self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("scenario_inc5", Attribute.DOUBLE, READ)

            self.city.addAttribute("rwht_incentive_2", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("rwht_incentive_5", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("incentive_outdoor", Attribute.DOUBLE, WRITE)

            # self.city.addAttribute("rwht_incentive", Attribute.DOUBLE, WRITE)


            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.city)
            # views.append(self.city)


            #Register ViewContainer to stream
            self.registerViewContainers(views)

            #Data Stream Definition


        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            self.city.reset_reading()
            incentive_outdoor = {}
            incentive_2 = {}
            incentive_5 = {}
            for i in range(1995, 2016):
                incentive_2[i] = 0
                incentive_5[i] = 0
                incentive_outdoor[i] = 0

            for key in incentive_outdoor:
                if key < 2002:
                    incentive_outdoor[key] = 0
                elif 2003 <= key < 2008:
                    incentive_outdoor[key] = 150
                elif key >= 2008:
                    incentive_outdoor[key]=0

            for key in incentive_2:
                if key < 2003:
                    incentive_2[key] = 0
                elif 2003 <= key < 2007:
                    incentive_2[key] = 300
                elif 2007 <= key < 2012:
                    incentive_2[key] = 500
                elif key >= 2012:
                    incentive_2[key]=950
            
            for key in incentive_5:
                if key < 2003:
                    incentive_5[key] = 0
                elif 2003 <= key < 2007:
                    incentive_5[key] = 300
                elif 2007 <= key < 2012:
                    incentive_5[key] = 900
                elif key >= 2012:
                    incentive_5[key] = 1400

            for b in self.city:
                year = b.GetFieldAsInteger("year")
                if year <= 2015:
                    b.SetField("rwht_incentive_2", incentive_2[year])
                    b.SetField("rwht_incentive_5", incentive_5[year])
                    b.SetField("incentive_outdoor", incentive_outdoor[year])
                else:
                    scenario_inc5 = b.GetFieldAsDouble("scenario_inc5")
                    # b.SetField("rwht_incentive_2", self.scenario_inc2)
                    b.SetField("rwht_incentive_5", scenario_inc5)
                    # b.SetField("incentive_outdoor", self.scenario_inc_out)

            self.city.finalise()
            # self.city.finalise()
