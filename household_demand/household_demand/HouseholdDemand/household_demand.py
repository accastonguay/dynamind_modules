__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *



class HouseholdDemand(Module):
        display_name = "Household demand"
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


            self.household = ViewContainer("household", COMPONENT, READ)

            self.household.addAttribute("raintank", Attribute.INT, READ)
            self.household.addAttribute("persons", Attribute.INT, READ)
            self.household.addAttribute("demand", Attribute.DOUBLE, WRITE)


            #Compile views
            views = []
            # views.append(self.city_council)
            views.append(self.household)
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
            self.household.reset_reading()
            # self.city_environment.reset_reading()
            for b in self.household:
                raintank = b.GetFieldAsInteger("raintank")
                persons = b.GetFieldAsDouble("persons")

                if raintank == 0:
                    b.SetField("demand", 0.00016*persons)

                elif raintank == 1:
                    b.SetField("demand", 0.00016*0.3*persons)



            self.household.finalise()
            # self.city_environment.finalise()