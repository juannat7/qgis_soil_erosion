# Quickstart Guide
1. Download QGIS 2.18 (stable version)
2. Open QGIS → Plugin → Manage & Install Plugin → Setting → Check ‘Show also experimental plugin’ → ‘Add’ plugin repository and fill the following:

Name: garuda-gis

URL: https://stg.gis.garuda.io/soil-erosion/gr_ser.xml

Keep other default as it is

3. Under ‘All’, find Garuda_Soil Erosion Risk and install the plugin
4. Open the plugin and browse to the directory that holds sample input data obtained here. 
5. Done! We appreciate any reviews which can be written here.


# Brief Description
Soil Erosion Risk Assessment (‘SRA’) QGIS Plugin is developed to automate the calculation, analysis, and evaluation processes to produce actionable map output that identifies locations prone to soil erosion. The methodologies adopted for this SRA plugin are modeled after the Revised Universal Soil Loss Equation (RUSLE), one of the few soil erosion models that prioritizes the use of geospatial inputs, rather than on-site samples, as key parameters.

Among the six parameters identified by RUSLE (land use, precipitation, slope angle, slope length, management practice, and soil erodibility), this plugin will evaluate four, excluding slope length and land use, primarily due to the lack of accurate algorithm to evaluate slope length and the inherent inaccuracy of automated classification of land use without manual supervision respectively.

# Data Input Preparation
Three data inputs will be needed to successfully run the plugin:

1. Boundary of study site (.shp)
2. Elevation data (.tif) - eg. DEM, aerial drone imagery with elevation data
3. Rainfall data (.csv) - precipitation level as measured from known coordinates

For rainfall data input, the following preparation needs to be followed so as to ensure proper working of the plugin

1. First column (‘x’) is the field to key in longitude (in degree) of the places where rain measurements are done
2. Second column (‘y’) is the field to key in latitude (in degrees) of the places where rain measurements are done
3. Third row onwards are the fields to key in precipitation level (in mm). ​Do note the formatting on how to write the field heading: ‘time’ followed by integers increasing from 1, no whitespace 
4. The projection assumed in this model is the standard WGS84. If your coordinates use different projections, please convert it to WGS84’s projection.

# Installation
Disclaimer: QGIS 2.18 (stable version) or newer is needed to run the plugin. 

1. Open QGIS
2. Under ​​Plugin → ​Manage and Install Plugins… → Setting, enable ‘Show also experimental plugins’
3. Under ‘Plugin repositories’ click ​Add. Fill the fields 
4. Find‘Garuda_Soil Erosion Risk’ to install the plugin
5. Now Garuda_Soil Erosion Risk will appear if you reopen Plugin tab. Open the Plugin

# Using the Plugin
This section assumed the data needed as in Section II have been prepared

1. Browse to the respective directories where the three input files are located (refer to Figure 4) for the first three fields (‘Boundary Shapefile’, ‘DEM Raster’, and Rainfall Data’)
2. Browse to a file directory to indicate where the output files will be located under ‘Output Directory’.
3. Select the ‘Soil Type’ and ‘Management Practice’ that best matches the site (​Disclaimer: only relevant to Malaysia’s soil as published by the Department of Agriculture) on the last two dropdown boxes.

4. Press ‘OK’ when done.
