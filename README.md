# NDVI-Viewer

View and compare NDVI values of an area of interest between two time periods.
Streamlit App: https://ndvi-viewer.streamlit.app/

### User guide

- Create shapefile of your area of interest in GeoJSON format by going to [geojson.io](https://geojson.io/) and drawing polygon shapes then exporting it to your local machine. From there you can drag-and-drop the GeoJSON file to the app upload section and it'll serve as area of interest to which all images will be clipped.
- Select Date Range: Pick the dates that you wish to compare NDVI values for. The app will calculate a 7-days range going back from each of the dates you picked.
- Select Cloud Coverate Rate: Set the cloude coverage value for better quality images or for larger dataset in your image collection.
- Additionally, for people with colorblind disability, it is possible to pick a color palette that's colorblind friendly with most common colorblindness types.

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

The app was developped by [IndigoWizard](https://github.com/IndigoWizard) and [Emmarie-Ahtunan](https://github.com/Emmarie-Ahtunan) using; Streamlit, Google Earth Engine Python API, geemap, Folium. Agriculture icons created by <a href="https://www.flaticon.com/free-icons/agriculture" title="agriculture icons">dreamicons - Flaticon</a>
