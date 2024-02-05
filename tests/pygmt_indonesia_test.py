import pygmt
import numpy as np
# # define user variables
# REGION = [109,117,-9,-6]
# MEAN_LON = int(np.round((REGION[0]+REGION[1])/2))
# MEAN_LAT = int(np.round((REGION[2]+REGION[3])/2))
# PROJECTION = "M20c"
# PERSPECTIVE = [165,30]
# ZSIZE = "1c"
# SHADING = True
# PROJECTION_INSET = f"M5c"
# AREA_THRESH = 10_000
#
# # download topo data at 30 arc sec. resolution
# grid = pygmt.datasets.load_earth_relief(resolution="30s",region=REGION)
#
# fig = pygmt.Figure()
# fig.grdview(grid=grid,
#             perspective=PERSPECTIVE,
#             frame=["xa","ya","WSnE"],
#             projection=PROJECTION,
#             zsize=ZSIZE,
#             surftype="s",
#             cmap="geo",
#             shading=SHADING,
#             )
# with fig.inset(position="jBL+o0.1c",
#                box="+gwhite+p1p",
#                region="Indonesia",
#                projection=PROJECTION_INSET,
#                ):
#     fig.coast(land="gray",
#               shorelines="0.1p",
#               dcw="ID+glightbrown+p0.2p",
#               area_thresh=AREA_THRESH,
#               )
#     fig.plot(data=[[REGION[0]-1,REGION[2]-1,REGION[1]+1,REGION[3]+1]],
#              style="r+s",
#              pen="2p,red",
#              )
#
# fig.show()


REGION = [10,30,76,81,-4000,2000]
MEAN_LON = int(np.round((REGION[0]+REGION[1])/2))
MEAN_LAT = int(np.round((REGION[2]+REGION[3])/2))
PROJECTION = "S0/90/20c"
PERSPECTIVE = [180,30]
ZSIZE = "0.5c"
SHADING = True
PROJECTION_INSET = f"M5c"
AREA_THRESH = 10_000

# download topo data at 30 arc sec. resolution
grid2 = pygmt.datasets.load_earth_relief(resolution="15s",region=REGION)

fig = pygmt.Figure()
fig.grdview(grid=grid2,
            perspective=PERSPECTIVE,
            frame=["xa","ya","WSnE"],
            projection=PROJECTION,
            zsize=ZSIZE,
            surftype="s",
            cmap="geo",
            shading=SHADING,
            plane="-6000+gazure",
            )

fig.plot3d(
        x = 78.925,
        y = 11.922222,
        z = 200,
        style ='c0.2c',
        color='red',
        pen = 'black',
        perspective=PERSPECTIVE,
        )
# fig.plot(x=78.925, y=11.922222,style='a0.5c',pen="1p,red")

fig.show()
