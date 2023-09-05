# NDVI-Viewer

View and compare NDVI values of an area of interest between two time periods.

### User guide

You can create area of interest shapefiles in GeoGSON format by going to [geojson.io](geojson.io) and drawing a polygon shape then exporting it to your local machine. From there you can drag-and-drop the GeoJSON file to the app upload section and it'll serve as area of interest to which all images will be clipped.

### Project structure

```
  ├── .github
  │   └── Contributing / PR template
  ├── .gitignore
  ├── app.py
  ├── requirements.txt
  └── README
```


### About

This project was first developed as a submission to the Environemental Data Challenge of [Global Hack Week: Data](https://ghw.mlh.io/) by [Major League Hacking](https://github.com/MLH). 

![](https://www.pixenli.com/image/Hn1xkB-6)

### Credit

The app was developped by [IndigoWizard](https://github.com/IndigoWizard) and [Emmarie-Ahtunan](https://github.com/Emmarie-Ahtunan) using; Streamlit, Google Earth Engine Python API, geemap, Folium.
