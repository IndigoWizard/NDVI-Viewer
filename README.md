# NDVI-Viewer

Monitor Vegetation Health by Viewing & Comparing NDVI Values Through Time and Location with Sentinel-2 Satellite Images on The Fly!
Streamlit App: https://ndvi-viewer.streamlit.app/

### User guide

- Create shapefile of your area of interest in GeoJSON format by going to [geojson.io](https://geojson.io/) and drawing polygon shapes then exporting it to your local machine. From there you can drag-and-drop the GeoJSON file to the app upload section and it'll serve as area of interest to which all images will be clipped.
- Select Date Range: Pick the dates that you wish to compare NDVI values for. The app will calculate a 7-days range going back from each of the dates you picked.
- Select Cloud Coverate Rate: Set the cloude coverage value for better quality images or for larger dataset in your image collection.
- Additionally, for people with colorblind disability, it is possible to pick a color palette that's colorblind friendly with most common colorblindness types.

### Preview:

![](https://www.pixenli.com/image/MeljR-zA)

### Note:

The app is hosted on Streamlit Cloud for free and has resource limit (1 GB), sometimes the app may crash when exceeding the limit (too many operations).

If the app crashes, it needs to be rebooted on dev end so DM me or rise an issue, no other options except deploying to a paid platform with padi resource increases.

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

The app was developped by [IndigoWizard](https://github.com/IndigoWizard) using; Streamlit, Google Earth Engine Python API, geemap, Folium. Agriculture icons created by <a href="https://www.flaticon.com/free-icons/agriculture" title="agriculture icons">dreamicons - Flaticon</a>

**Contributors**: [Emmarie-Ahtunan](https://github.com/Emmarie-Ahtunan)
