import streamlit as st
import ee
import geemap
import folium
from folium import WmsTileLayer
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import json

# Initializing the Earth Engine library
# Use ee.Initialize() only on local machine! Comment back before deployement (Unusable on deployment > use geemap init+auth bellow)
#ee.Initialize()
# geemap auth + initialization for cloud deployment
@st.cache_data(persist=True)
def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)

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

# Uplaod function 
def upload_files_proc(upload_files):
    geometry_aoi_list = []
    for upload_file in upload_files:
        bytes_data = upload_file.read()
        # Parse GeoJSON data
        geojson_data = json.loads(bytes_data)
        # Extract the coordinates from the GeoJSON data
        coordinates = geojson_data['features'][0]['geometry']['coordinates']
        # Creating gee geometry object based on coordinates
        geometry = ee.Geometry.Polygon(coordinates)
        # Adding geometry to the list
        geometry_aoi_list.append(geometry)
    # Combine multiple geometries from same/different files
    if geometry_aoi_list:
        geometry_aoi = ee.Geometry.MultiPolygon(geometry_aoi_list)
    else:
        # Set default geometry if no file uploaded
        geometry_aoi = ee.Geometry.Point([27.98, 36.13])
    return geometry_aoi

# Main function to run the Streamlit app
def main():
    # initiate gee 
    ee_authenticate(token_name="EARTHENGINE_TOKEN")

    st.title('NDVI Viewer Streamlit App')

    #### User input section - START
    st.write("Choose a GeoJSON file for your Area Of Interest:")
    ## File upload
    # User input GeoJSON file
    upload_files = st.file_uploader("Choose a GeoJSON file", accept_multiple_files=True, label_visibility ="collapsed")
    # calling upload files function
    geometry_aoi = upload_files_proc(upload_files)

    ## Time range inpui
    # time input goes here
    
    col1, col2 = st.columns(2)

    col1.info("Old NDVI Date 📅")
    old_date = col1.date_input("old", datetime(2023, 3, 20), label_visibility="collapsed")

    col2.success("New NDVI Date 📅")
    new_date = col2.date_input("new", datetime(2023, 7, 17), label_visibility="collapsed")

    # Calculating time frame
    # time stretch
    days_before = 7
    # old time range
    old_start_date = old_date - timedelta(days=days_before)
    old_end_date = old_date

    # new time range
    new_start_date = new_date - timedelta(days=days_before)
    new_end_date = new_date

    # converting date input to gee filter format before passing it in
    # old
    str_old_start_date = old_start_date.strftime('%Y-%m-%d')
    str_old_end_date = old_end_date.strftime('%Y-%m-%d')
    # new
    str_new_start_date = new_start_date.strftime('%Y-%m-%d')
    str_new_end_date = new_end_date.strftime('%Y-%m-%d')

    #### User input section - END

    #### Map section - START
    # Setting up main map
    m = folium.Map(location=[36.45, 2.85], tiles='Open Street Map', zoom_start=9, control_scale=True)

    ### BASEMAPS - START
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
    ### BASEMAPS - END
    #### Map section - END

    #### Satellite imagery Processing Section - START
    # Old Image collection
    old_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 100)) \
    .filterDate(str_old_start_date, str_old_end_date) \
    .filterBounds(geometry_aoi)

    # New Image collection
    new_collection = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 100)) \
    .filterDate(str_new_start_date, str_new_end_date) \
    .filterBounds(geometry_aoi)

    # clipping the main collection to the aoi geometry
    old_clipped_collection = old_collection.map(lambda image: image.clip(geometry_aoi).divide(10000))
    new_clipped_collection = new_collection.map(lambda image: image.clip(geometry_aoi).divide(10000))
    
    # setting a sat_imagery variable that could be used for various processes later on (tci, ndvi... etc)
    old_sat_imagery = old_clipped_collection.median()
    new_sat_imagery = new_clipped_collection.median()

    ## TCI (True Color Imagery)
    # Clipping the image to the area of interest "aoi"
    old_tci_image = old_sat_imagery
    new_tci_image = new_sat_imagery

    # TCI image visual parameters
    tci_params = {
    'bands': ['B4', 'B3', 'B2'], #using Red, Green & Blue bands for TCI.
    'min': 0,
    'max': 1,
    'gamma': 1
    }

    ## Other imagery processing operations go here 
    # NDVI
    def getNDVI(collection):
        return collection.normalizedDifference(['B8', 'B4'])

    # clipping to AOI
    old_ndvi = getNDVI(old_sat_imagery)
    new_ndvi = getNDVI(new_sat_imagery)

    # NDVI visual parameters:
    ndvi_params = {
    'min': 0,
    'max': 1,
    'palette': ['#ffffe5', '#f7fcb9', '#78c679', '#41ab5d', '#238443', '#005a32']
    }

    # Masking NDVI over the water & show only land
    old_ndvi = old_ndvi.updateMask(old_ndvi.gte(0))
    new_ndvi = new_ndvi.updateMask(new_ndvi.gte(0))

    # ##### NDVI classification: 7 classes
    old_ndvi_classified = ee.Image(old_ndvi) \
    .where(old_ndvi.gte(0).And(old_ndvi.lt(0.15)), 1) \
    .where(old_ndvi.gte(0.15).And(old_ndvi.lt(0.25)), 2) \
    .where(old_ndvi.gte(0.25).And(old_ndvi.lt(0.35)), 3) \
    .where(old_ndvi.gte(0.35).And(old_ndvi.lt(0.45)), 4) \
    .where(old_ndvi.gte(0.45).And(old_ndvi.lt(0.65)), 5) \
    .where(old_ndvi.gte(0.65).And(old_ndvi.lt(0.75)), 6) \
    .where(old_ndvi.gte(0.75), 7) \
    
    # ##### NDVI classification: 7 classes
    new_ndvi_classified = ee.Image(new_ndvi) \
    .where(new_ndvi.gte(0).And(new_ndvi.lt(0.15)), 1) \
    .where(new_ndvi.gte(0.15).And(new_ndvi.lt(0.25)), 2) \
    .where(new_ndvi.gte(0.25).And(new_ndvi.lt(0.35)), 3) \
    .where(new_ndvi.gte(0.35).And(new_ndvi.lt(0.45)), 4) \
    .where(new_ndvi.gte(0.45).And(new_ndvi.lt(0.65)), 5) \
    .where(new_ndvi.gte(0.65).And(new_ndvi.lt(0.75)), 6) \
    .where(new_ndvi.gte(0.75), 7) \

    # Classified NDVI visual parameters
    ndvi_classified_params = {
    'min': 1,
    'max': 7,
    'palette': ['#a50026', '#ed5e3d', '#f9f7ae', '#fec978', '#9ed569', '#229b51', '#006837']
    # each color corresponds to an NDVI class.
    }

    #### Satellite imagery Processing Section - END

    #### Layers section - START
    # basemap layers
    m.add_ee_layer(old_tci_image, tci_params, 'Old Satellite Imagery')
    m.add_ee_layer(new_tci_image, tci_params, 'New Satellite Imagery')

    # NDVI
    m.add_ee_layer(old_ndvi, ndvi_params, 'Old Raw NDVI')
    m.add_ee_layer(new_ndvi, ndvi_params, 'New Raw NDVI')

    # Add layers to the second map (m.m2)
    # Classified NDVI
    m.add_ee_layer(old_ndvi_classified, ndvi_classified_params, 'Old Reclassified NDVI')
    m.add_ee_layer(new_ndvi_classified, ndvi_classified_params, 'New Reclassified NDVI')

    #### Layers section - END

    #### Map result display - START
    # Folium Map Layer Control: we can see and interact with map layers
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Display the map
    folium_static(m)

    #### Map result display - END

    #### Legend - START
    st.write("### Map Legend:")

    # Define classified NDVI color palette hex codes
    classified_ndvi_palette = ['#a50026', '#ed5e3d', '#f9f7ae', '#fec978', '#9ed569', '#229b51', '#006837']

    # Create an HTML legend for NDVI classes
    classified_ndvi_legend_html = """
        <div style="border-radius: 5px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);">
            <h5>Reclassified NDVI</h5>
            <ul style="list-style-type: none; padding: 0;">
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {0};">&#9632;</span> [-1 ; 0.15] Absent Vegetation. (Water/Built-up/Rocky/Sandy Surfaces..)</li>
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {1};">&#9632;</span> [0.15 ; 0.25] Bare Soil.</li>
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {2};">&#9632;</span> [0.25 ; 0.35] Low Vegetation.</li>
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {3};">&#9632;</span> [0.35 ; 0.45] Light Vegetation.</li>
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {4};">&#9632;</span> [0.45 ; 0.65] Moderate Vegetation.</li>
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {5};">&#9632;</span> [0.65 ; 0.75] Strong Vegetation.</li>
                <li style="margin: 0.2em 0px; padding: 0;"><span style="color: {6};">&#9632;</span> [> 0.75 ] Dense Vegetation.</li>
            </ul>
        </div>
    """.format(*classified_ndvi_palette)

    # Display the Reclassified NDVI legend using st.markdown
    st.markdown(classified_ndvi_legend_html, unsafe_allow_html=True)
    #### Legend - END

    #### Miscs Infos - START
    st.write("### Information")

    st.write("The **[Normalized Difference Vegetation Index (NDVI)](https://eos.com/make-an-analysis/ndvi/)** is a widely used indicator of vegetation health and density. It quantifies the presence of green vegetation by measuring the difference between near-infrared (NIR) and red (R) reflectance of the Earth's surface. NDVI values range from -1 to 1, where higher values typically indicate denser and healthier vegetation.")

    st.write("NDVI is calculated using the formula:")
    st.latex(r'''
    \text{NDVI} = \frac{\text{NIR} - \text{R}}{\text{NIR} + \text{R}}
    ''')

    st.write("In this application, we utilize **Sentinel-2 Level-2A atmospherically corrected Surface Reflectance images**. These images are acquired by the [Sentinel-2 satellite constellation](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/applications), which consists of twin satellites (Sentinel-2A and Sentinel-2B) that capture high-resolution multispectral imagery of the Earth's surface.")

    st.write("The [Level-2A](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/product-types/level-2a) products have undergone atmospheric correction, which removes the effects of the atmosphere on the captured radiance. This correction enhances the accuracy of the surface reflectance values, making them suitable for various land cover and vegetation analysis, including NDVI calculations.")

    # Note on Image Interpretation
    st.write("### Note on Image Interpretation")

    st.write("The NDVI map displayed above provides insights into the vegetation distribution. However, please be aware of the following factors that can affect the map's appearance into displaying data:")

    st.write("1. **Clouds and Atmospheric Effects:** Clouds and atmospheric conditions can impact NDVI calculations, leading to unexpected color variations in the map.")
    st.write("2. **Water Bodies:** Some water bodies might exhibit higher NDVI values due to their reflectance properties, leading to color patterns that differ from expected vegetation patterns.")
    st.write("3. **Sensor Limitations:** Satellite sensors have limitations in distinguishing between surface types, leading to variations in NDVI values and colors.")
    st.write("4. **Seasonal Changes:** NDVI values can vary based on seasonal changes, vegetation growth stages, and natural fluctuations in land cover.")
    st.write("5. **Data Processing:** The displayed NDVI values result from complex data processing and analysis techniques, providing visual aids rather than precise representations.")

    st.write("As you explore the NDVI map, understanding these influences will help you interpret the results more effectively and make informed decisions based on the insights gained.")

    st.write("Please use this information as a guide to understanding the potential variations in the NDVI map and the factors that contribute to its visual representation.")

    #### Miscs Info - END


 

# Run the app
if __name__ == "__main__":
    main()
