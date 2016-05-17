__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *



class subsidies(Module):
        display_name = "Subsidies"
        group_name = "Decisions"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            # self.createParameter("restriction", INT)


            self.city = ViewContainer("city", COMPONENT, READ)

            self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("rwht_incentive_2", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("rwht_incentive_5", Attribute.DOUBLE, WRITE)

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

            #print self.my_parameter

            #Data Stream Manipulation

            #print self.my_parameter
            self.city.reset_reading()

            incentive_2 = {}
            incentive_5 = {}
            for i in range(1995, 2016):
                incentive_2[i] = 0
                incentive_5[i] = 0

            for key in incentive_2:
                if key < 2002:
                    incentive_2[key] = 0
                elif 2002 <= key < 2005:
                    incentive_2[key] = 150
                elif 2005 <= key < 2009:
                    incentive_2[key] = 300
                elif 2009 <= key < 2012:
                    incentive_2[key]= 500
                elif key >= 2012:
                    incentive_2[key]=900
            
            for key in incentive_5:
                if key < 2002:
                    incentive_5[key] = 0
                elif 2002 <= key < 2005:
                    incentive_5[key] = 150
                elif 2005 <= key < 2009:
                    incentive_5[key] = 300
                elif 2009 <= key < 2012:
                    incentive_5[key] = 1000
                elif key >= 2012:
                    incentive_5[key] = 1500

            # for key in dict:
            #     if key < 2009:
            #         dict[key] = 300
            #     elif 2009 <= key < 2012:
            #         dict[key]= 750
            #     elif key >= 2012:
            #         dict[key]=1175

            for b in self.city:
                year = b.GetFieldAsInteger("year")
                # b.SetField("rwht_incentive_2", dict2[year])
                # b.SetField("rwht_incentive_5", dict5[year])
                # b.SetField("rwht_incentive", dict[year])
                b.SetField("rwht_incentive_2", incentive_2[year])
                b.SetField("rwht_incentive_5", incentive_5[year])

            self.city.finalise()
            # self.city.finalise()