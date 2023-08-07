import ee
from ee import image
import folium
from folium import WmsTileLayer
import webbrowser

# command line > activate environement > earthengine authenticate
# Or: Uncomment then execute only once to authenticate (put back as comment)
#ee.Authenticate()

# initializing the earth engine library
ee.Initialize()

# ##### earth-engine drawing method setup
def add_ee_layer(self, ee_image_object, vis_params, name):
  map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
  layer = folium.raster_layers.TileLayer(
      tiles = map_id_dict['tile_fetcher'].url_format,
      attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name = name,
      overlay = True,
      control = True
  )
  layer.add_to(self)
  return layer

# configuring earth engine display rendering method in folium
folium.Map.add_ee_layer = add_ee_layer

# setting up main map
m = folium.Map(location = [36.8, 3.0], tiles='Open Street Map', zoom_start = 5, control_scale = True)

##### BASEMAPS
### Primary basemaps
b1 = folium.TileLayer('cartodbdark_matter', name='Dark Matter Basemap')

### WMS tiles basemaps
b2 = WmsTileLayer(
  url=('https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png'),
  layers=None,
  name='Topography Map',
  attr='Topography Map',
  show=False
).add_to(m)


# Folium Map Layer Control: we can see and interact with map layers
folium.LayerControl(collapsed=False).add_to(m)

# saving output file as html
m.save('index.html')

# openning map file in default browser
webbrowser.open('index.html')