import folium
from folium import WmsTileLayer
import webbrowser

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

# saving output file as html
m.save('index.html')

# openning map file in default browser
webbrowser.open('index.html')