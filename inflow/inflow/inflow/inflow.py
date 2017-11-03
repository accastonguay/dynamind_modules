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

            self.createParameter("rule", INT)
            self.rule = 1


            self.city = ViewContainer("city", COMPONENT, READ)

            self.city.addAttribute("year", Attribute.INT, READ)
            self.city.addAttribute("inflow", Attribute.DOUBLE, WRITE)



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
            # self.city.reset_reading()

            dict = {1995:666.737, 1996:826.375, 1997:231.941, 1998:432.954, 1999:316.984, 2000:560.063, 2001:426.363, 2002:324.202, 2003:508.84, 2004:507.961, 2005:389.269, 2006:163.24, 2007:374.236, 2008:287.465, 2009:368.941, 2010:559.363, 2011:633.776, 2012:658.286, 2013:415.665, 2014:420.935, 2015:306.2582}

            for b in self.city:
                if self.rule == 1:
                    year = b.GetFieldAsInteger("year")
                    # print 'year is: '+str(year)+ ' ; inflow is: ' + str(dict[year])
                    b.SetField("inflow", dict[year])

                elif self.rule == 2:
                    inf = randrange(150,700)
                    b.SetField("inflow", inf)



            self.city.finalise()
            # self.city.finalise()
