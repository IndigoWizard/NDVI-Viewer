import streamlit as st
import ee
import folium
from folium import WmsTileLayer
from streamlit_folium import folium_static
import json

# Initializing the Earth Engine library
ee.Initialize()

# Earth Engine drawing method setup
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    layer = folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    )
    layer.add_to(self)
    return layer

# Configuring Earth Engine display rendering method in Folium
folium.Map.add_ee_layer = add_ee_layer

aoi = ee.Geometry.Point([2.80, 36.40]).buffer(20000)

# Main function to run the Streamlit app
def main():
    st.title('Earth Engine Streamlit App')
    #### Map section
    # Setting up main map
    m = folium.Map(location=[36.40, 2.80], tiles='Open Street Map', zoom_start=10, control_scale=True)

    ### BASEMAPS
    ## Primary basemaps
    # CartoDB Dark Matter basemap
    b1 = folium.TileLayer('cartodbdark_matter', name='Dark Matter Basemap')
    b1.add_to(m)

    ## WMS tiles basemaps
    # OSM CyclOSM basemap 
    b2 = WmsTileLayer(
        url=('https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png'),
        layers=None,
        name='Topography Basemap', # layer name to display on layer panel
        attr='Topography Map',
        show=False
    )
    b2.add_to(m)

    #### Satellite imagery Processing Section
    # Specific satellite image ID (july 2023 - North of Algeria)
    tci_image = ee.Image('COPERNICUS/S2/20230713T102649_20230713T103541_T31SDA')
    
    # Clipping the image to the area of interest "aoi"
    tci_image_clipped = tci_image.clip(aoi).divide(10000)
    
    # TCI image visual parameters
    tci_params = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0.1,
        'max': 0.5,
        'gamma': 1
    }

    #### Layers section
    # add TCI layer to map
    m.add_ee_layer(tci_image_clipped, tci_params, 'S2 TCI - July 2023')

    #### Map result display
    # Folium Map Layer Control: we can see and interact with map layers
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Display the map
    folium_static(m)

# Run the app
if __name__ == "__main__":
    main()
