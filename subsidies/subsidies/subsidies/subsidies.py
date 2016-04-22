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
            # self.city.addAttribute("rwht_incentive_2", Attribute.DOUBLE, WRITE)
            # self.city.addAttribute("rwht_incentive_5", Attribute.DOUBLE, WRITE)

            self.city.addAttribute("rwht_incentive", Attribute.DOUBLE, WRITE)


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

            # dict2 = {1995:0, 1996:0, 1997:0, 1998:0, 1999:0, 2000:0, 2001:0, 2002:0, 2003:0, 2004:507.961, 2005:389.269, 2006:163.24, 2007:374.236, 2008:287.465, 2009:368.941, 2010:559.363, 2011:633.776, 2012:658.286, 2013:415.665, 2014:420.935, 2015:306.2582}
            # dict5 = {1995:0, 1996:0, 1997:0, 1998:0, 1999:0, 2000:0, 2001:0, 2002:0, 2003:0, 2004:507.961, 2005:389.269, 2006:163.24, 2007:374.236, 2008:287.465, 2009:368.941, 2010:559.363, 2011:633.776, 2012:658.286, 2013:415.665, 2014:420.935, 2015:306.2582}
            dict = {1995:0, 1996:0, 1997:0, 1998:0, 1999:0, 2000:0, 2001:0, 2002:0, 2003:0, 2004:507.961, 2005:389.269, 2006:163.24, 2007:374.236, 2008:287.465, 2009:368.941, 2010:559.363, 2011:633.776, 2012:658.286, 2013:415.665, 2014:420.935, 2015:306.2582}

            # for key in dict2:
            #     if key < 2009:
            #         dict2[key] = 0
            #     elif 2009 <= key < 2012:
            #         dict2[key]= 500
            #     elif key >= 2012:
            #         dict2[key]=900
            #
            # for key in dict5:
            #     if key < 2009:
            #         dict5[key] = 0
            #     elif 2009 <= key < 2012:
            #         dict5[key]= 1000
            #     elif key >= 2012:
            #         dict5[key]=1500
            for key in dict:
                if key < 2009:
                    dict[key] = 300
                elif 2009 <= key < 2012:
                    dict[key]= 750
                elif key >= 2012:
                    dict[key]=1175

            for b in self.city:
                year = b.GetFieldAsInteger("year")
                # b.SetField("rwht_incentive_2", dict2[year])
                # b.SetField("rwht_incentive_5", dict5[year])
                b.SetField("rwht_incentive", dict[year])


            self.city.finalise()
            # self.city.finalise()