# NDVI-Viewer

View and compare NDVI values of an area of interest between two time periods.

### User guide

You can create area of interest shapefiles in GeoGSON format by going to [geojson.io](geojson.io) and drawing a polygon shape then exporting it to your local machine. From there you can drag-and-drop the GeoJSON file to the app upload section and it'll serve as area of interest to which all images will be clipped.

### Project structure

```
  ├── .gitignore
  ├── app.py
  ├── src
  │   └── styling files
  ├── requirements.txt
  └── README
```


### About

This project was first developed as a submission to the Environemental Data Challenge of [Global Hack Week: Data](https://ghw.mlh.io/) by [Major League Hacking](https://github.com/MLH). 


<div style="display: flex; width: 100%;">
    <div style="flex: 22%; margin-right:5px;">
        <img src="https://cdn.discordapp.com/attachments/1134523742245097482/1137799138541580381/image.png" alt="ENVCHALLENGE" style="width:100%; height:auto;">
    </div>
    <div style="flex: 50%; margin-left:5px;">
        <img src="https://user-images.githubusercontent.com/57787993/258729929-52b7e6da-aa73-4ebb-914d-ea22df58acd4.png" alt="GHWDATA" style="width:100%; height:auto;">
    </div>
</div>

### Credit

The app was developped by [IndigoWizard](https://github.com/IndigoWizard) and [Emmarie-Ahtunan](https://github.com/Emmarie-Ahtunan) using; Streamlit, Google Earth Engine Python API, geemap, Folium.