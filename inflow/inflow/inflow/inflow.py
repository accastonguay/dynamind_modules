__author__ = 'acharett'


from pydynamind import *
from osgeo import ogr
from random import *

class inflow(Module):
        display_name = "inflow"
        group_name = "ABM"
        """
        Module Initialisation
        """
        def __init__(self):
            Module.__init__(self)

            #To use the GDAL API
            self.setIsGDALModule(True)
            #Parameter Definition

            self.city = ViewContainer("city", COMPONENT, READ)
            self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("inflow", Attribute.DOUBLE, WRITE)
            self.city.addAttribute("inf_scenario", Attribute.INT, READ)

            #Compile views
            views = []
            views.append(self.city)
            self.registerViewContainers(views)

        """
        Data Manipulation Process (DMP)
        """

        def run(self):
            #Data Stream Manipulation

            self.city.reset_reading()

            dict = {1995:666.737, 1996:826.375, 1997:231.941, 1998:432.954, 1999:316.984, 2000:560.063, 2001:426.363, 2002:324.202, 2003:508.84, 2004:507.961, 2005:389.269, 2006:163.24, 2007:374.236, 2008:287.465, 2009:368.941, 2010:559.363, 2011:633.776, 2012:658.286, 2013:415.665, 2014:420.935, 2015:306.2582}

            for c in self.city:
                year = c.GetFieldAsInteger("year")

                if year <= 2015:
                    c.SetField("inflow", dict[year])
                else:
                    inf_scenario = c.GetFieldAsInteger("inf_scenario")
                    if inf_scenario == 1:
                        inflow = 500*(1-0.001022675)**(year-2015)
                        inf = randrange(int(inflow - inflow*0.2),int(inflow + inflow*0.2))
                        c.SetField("inflow", inf)
                    elif inf_scenario == 2:
                        inflow = 500*(1-0.004132097)**(year-2015)
                        inf = randrange(int(inflow - inflow*0.2),int(inflow + inflow*0.2))
                        c.SetField("inflow", inf)
                    elif inf_scenario == 3:
                        inflow = 500 * (1 -0.01463821) ** (year - 2015)
                        inf = randrange(int(inflow - inflow * 0.2), int(inflow + inflow * 0.2))
                        c.SetField("inflow", inf)

            self.city.finalise()
