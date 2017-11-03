from pydynamind import *
from osgeo import ogr

class WsudGrid(Module):
    display_name = "WSUD grid"
    group_name = "ABM"
    """
    Module Initialisation
    """

    def __init__(self):
        Module.__init__(self)

        # To use the GDAL API
        self.setIsGDALModule(True)
        # Parameter Definition

        # self.createParameter("p_temp_id", STRING)
        # self.p_temp_id = "ogc_fid0"

    def init(self):

        self.grid = ViewContainer("wsud_grid", COMPONENT, READ)

        # self.grid.addAttribute("conv_area", Attribute.DOUBLE, READ)
        self.grid.addAttribute("area", Attribute.DOUBLE, READ)

        self.grid.addAttribute("tech", Attribute.STRING, READ)
        self.grid.addAttribute("converted", Attribute.INT, WRITE)
        self.grid.addAttribute("parcel_id", Attribute.INT, READ)


        self.p_temp = ViewContainer("p_temp", COMPONENT, READ)

        self.p_temp.addAttribute("conv_area", Attribute.DOUBLE, READ)
        self.p_temp.addAttribute("parcel_id", Attribute.INT, READ)

        self.registerViewContainers([self.grid,self.p_temp])

    """
    Data Manipulation Process (DMP)
    """

    def run(self):
        # Data Stream Manipulation
        d = {}
        self.p_temp.reset_reading()
        for p in self.p_temp:
            c = p.GetFieldAsDouble("conv_area")
            id = p.GetFieldAsInteger("parcel_id")
            d[id] = c
        self.p_temp.finalise()

        self.grid.reset_reading()

        converted_sofar = {}

        for i in d:
            converted_sofar[i] = 0

        for g in self.grid:
            # c = g.GetFieldAsDouble("conv_area")
            a = g.GetFieldAsDouble("area")
            id = g.GetFieldAsInteger("parcel_id")
            # print "area", a
            # print "id", id
            if converted_sofar[id] + a < d[id]:
                # print "still space", str(converted_sofar[id] + a), str(d[id])
                # print d
                g.SetField("converted", 1)
                converted_sofar[id] += a
            #     print "converted sofar", converted_sofar
            # else:
            #     print "no more space"

        self.grid.finalise()


