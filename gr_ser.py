# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GR_SER
                                 A QGIS plugin
 This plugin assesses soil risk based on RUSLE model
                              -------------------
        begin                : 2018-06-11
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Garuda Robotics
        email                : juan@garuda.io
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Python modules
import sys
import time
import os
import qgis

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, QSettings
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QApplication

from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsInterpolator, QgsIDWInterpolator, QgsGridFileWriter
from qgis.core import QgsRasterLayer, QgsVectorLayer, edit, QgsFeatureRequest, QgsMapLayerRegistry, QgsApplication
import qgis.analysis
import qgis.utils

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from gr_ser_dialog import GR_SERDialog
import os.path
from qgis.core import *
from qgis.core import QgsField, QgsExpression, QgsFeature
from qgis.gui import *
from qgis.utils import iface
from processing.tools.vector import VectorWriter
from qgis.PyQt.QtCore import QVariant

import processing
import numpy as np
from osgeo import gdal

class GR_SER:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GR_SER_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = GR_SERDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GR - Soil Risk Assessment')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GR_SER')
        self.toolbar.setObjectName(u'GR_SER')

        # Upon pushButton clicked
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_boundary_file)

        self.dlg.lineEdit_2.clear()
        self.dlg.pushButton_2.clicked.connect(self.select_dem_file)

        self.dlg.lineEdit_3.clear()
        self.dlg.pushButton_3.clicked.connect(self.select_rainfall_file)

        self.dlg.lineEdit_4.clear()
        self.dlg.pushButton_4.clicked.connect(self.select_output_directory)

        # Add raster


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GR_SER', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        '''self.dlg = GR_SERDialog()'''

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GR_SER/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GR - Soil Erosion Risk'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GR - Soil Risk Assessment'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_boundary_file(self):
        boundary_input = QFileDialog.getOpenFileName(self.dlg, "Boundary Shapefile ","", '*.shp')
        self.dlg.lineEdit.setText(boundary_input)

    def select_dem_file(self):
        dem_input = QFileDialog.getOpenFileName(self.dlg, "DEM Raster ","", '*.tif')
        self.dlg.lineEdit_2.setText(dem_input)

    def select_rainfall_file(self):
        rainfall_input = QFileDialog.getOpenFileName(self.dlg, "Rainfall Data","", '*.csv')
        self.dlg.lineEdit_3.setText(rainfall_input)

    def select_output_directory(self):
        output_directory = QFileDialog.getExistingDirectory(self.dlg, "Output Directory ","")
        self.dlg.lineEdit_4.setText(output_directory)


    def k_list(self):

        k_list = ["Asahan",
                  "Akob",
                  "Alma",
                  "Apek",
                  "Alor Semat",
                  "Awang",
                  "Bukit Ajil",
                  "Benda Nyior",
                  "Bemban",
                  "Berinchang",
                  "Belading",
                  "Badak",
                  "Bedup",
                  "Beoh",
                  "Baging"]

        return k_list

    def k_index(self, index):

        k_index = [0.002621,
                   0.002200,
                   0.002210,
                   0.002591,
                   0.002200,
                   0.003079,
                   0.002200,
                   0.002200,
                   0.002205,
                   0.002257,
                   0.002252,
                   0.002200,
                   0.002200,
                   0.002571]

        return k_index[index]

    def m_list(self):

        m_list = ["Planting Beds against/perpendicular to contour",
                  "Planting Beds along Contour",
                  "Grass Strip",
                  "Contour Ditches",
                  "Hillside Trench (Silt Trap)",
                  "Rain Shelter",
                  "Contour Planning",
                  "Mulching",
                  "Terraces (Continuous)",
                  "Terraces (Discontinuous)",
                  "Individual Basin",
                  "Traditional Terraces",
                  "Vertiver-Contour Hedgerow"]

        return m_list

    def m_index(self, index):

        m_index = [0.85,
                   0.3,
                   0.5,
                   0.5,
                   0.6,
                   0.1,
                   0.8,
                   0.2,
                   0.2,
                   0.4,
                   0.5,
                   0.6,
                   0.6]

        return m_index[index]

    def run(self):
        """Run method that performs all the real work"""
        # Add items to Management Practices & Soil Type
        k_lists = []
        m_lists = []

        k_lists = self.k_list()
        m_lists = self.m_list()



        self.dlg.comboBox.addItems(k_lists)
        self.dlg.comboBox_2.addItems(m_lists)

        # show dialog box
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # Save paths of input directories
            selectedBoundary = self.dlg.lineEdit.text()
            selectedDEM = self.dlg.lineEdit_2.text()
            selectedRLayer = self.dlg.lineEdit_3.text()

            selectedOutput = self.dlg.lineEdit_4.text()
            for letter in selectedOutput:
                if letter == "\\":
                    selectedOutput = selectedOutput.replace(letter, "/")

            print(selectedBoundary)
            print(selectedDEM)
            print(selectedRLayer)
            print(selectedOutput)

            # Save indices for K and M
            selectedKLayer = self.dlg.comboBox.currentIndex()
            selectedMLayer = self.dlg.comboBox_2.currentIndex()

            boundary = QgsVectorLayer(selectedBoundary, 'Boundary', 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer(boundary)

            entries = []

            # Retrieve K and M values

            k_value = self.k_index(selectedKLayer)
            m_value = self.m_index(selectedMLayer)

            km_value = k_value * m_value
            km_value = str(km_value)

            # Process R index

            ## CSV to Layer
            uri = 'file:///' + selectedRLayer + '?delimiter=%s&xField=%s&yField=%s&crs=%s' % (",", "x", "y", "EPSG:4326")
            rainfall_unedited = QgsVectorLayer(uri, "rainfall", "delimitedtext")
            QgsMapLayerRegistry.instance().addMapLayer(rainfall_unedited)
            spatRef = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

            ## CSV points to editable shapefile
            rainfall_edited = QgsVectorFileWriter(selectedOutput + '/rainfall_edited.shp', None, rainfall_unedited.pendingFields(), QGis.WKBPoint, spatRef)

            pt = QgsPoint()
            outFeature = QgsFeature()

            for feat in rainfall_unedited.getFeatures():
                attrs = feat.attributes()
                pt.setX(feat['x'])
                pt.setY(feat['y'])
                outFeature.setAttributes(attrs)
                outFeature.setGeometry(QgsGeometry.fromPoint(pt))
                rainfall_edited.addFeature(outFeature)
            del rainfall_edited

            rainfall_edited2 = QgsVectorLayer(selectedOutput +'/rainfall_edited.shp', 'rainfall_edited', 'ogr')

            ## Add and calculate average field
            rainfall_edited2.startEditing()

            avgField = QgsField('average', QVariant.Double)
            rainfall_edited2.dataProvider().addAttributes([avgField])
            rainfall_edited2.updateFields()
            idx = rainfall_edited2.fieldNameIndex('average')

            time_count = idx - 2
            str_output = ''
            for i in range(1, time_count+1):
                if i == 1:
                    a = str(i)
                    str_output += 'time' + a

                else:
                    a = str(i)
                    str_output += '+ time' + a

            e = QgsExpression(str_output)
            e.prepare(rainfall_edited2.pendingFields())

            for f in rainfall_edited2.getFeatures():
                f[idx] = e.evaluate(f) / time_count
                rainfall_edited2.updateFeature(f)

            rainfall_edited2.commitChanges()

            rainfall_edited3 = QgsVectorLayer(selectedOutput + '/rainfall_edited.shp', 'rainfall_edited', 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer(rainfall_edited3)

            ## Interpolating average using IDW
            ### Parameters for interpolation
            idx = rainfall_edited3.fieldNameIndex('average')

            layer_data = qgis.analysis.QgsInterpolator.LayerData()
            layer_data.vectorLayer = rainfall_edited3
            layer_data.zCoordInterpolation = False
            layer_data.interpolationAttribute = idx
            layer_data.mInputType = 1

            idw_interpolator = QgsIDWInterpolator([layer_data])

            ### Output parameter
            export_path = selectedOutput + "/interpolated_r_{}.asc".format(idx)
            rect = boundary.extent()
            res = 0.0001
            ncol = (rect.xMaximum() - rect.xMinimum()) / res
            nrows = (rect.yMaximum() - rect.yMinimum()) / res

            interpolated_r = QgsGridFileWriter(idw_interpolator, export_path, rect, int(ncol), int(nrows), res, res)
            interpolated_r.writeFile(True)

            interpolated_r2 = QgsRasterLayer(export_path, "interpolated_r")

            ## Clip output to boundary
            clippedR = processing.runandload('gdalogr:cliprasterbymasklayer',
                             interpolated_r2,    #INPUT <ParameterRaster>
                             boundary,     #MASK <ParameterVector>
                             "-9999",  #NO_DATA <ParameterString>
                             False,    #ALPHA_BAND <ParameterBoolean>
                             False,    #CROP_TO_CUTLINE <ParameterBoolean>
                             False,    #KEEP_RESOLUTION <ParameterBoolean>
                             5,        #RTYPE <ParameterSelection>
                             4,        #COMPRESS <ParameterSelection>
                             1,        #JPEGCOMPRESSION <ParameterNumber>
                             6,        #ZLEVEL <ParameterNumber>
                             1,        #PREDICTOR <ParameterNumber>
                             False,    #TILED <ParameterBoolean>
                             2,        #BIGTIFF <ParameterSelection>
                             False,    #TFW <ParameterBoolean>
                             "",       #EXTRA <ParameterString>
                             selectedOutput + '/clip_interpolated_r.tif') #OUTPUT <OutputRaster>

            r_layer = QgsRasterLayer(selectedOutput + '/clip_interpolated_r.tif', "R-index")
            boh4 = QgsRasterCalculatorEntry()
            boh4.ref = 'boh4@1'
            boh4.raster = r_layer
            boh4.bandNumber = 1
            entries.append(boh4)

            # Process S index
            ## Load DEM

            bohLayer1 = QgsRasterLayer(selectedDEM, "DEM")
            boh2 = QgsRasterCalculatorEntry()
            boh2.ref = 'boh2@1'
            boh2.raster = bohLayer1
            boh2.bandNumber = 1
            entries.append(boh2)

            ## Clip output to boundary
            clippedOutput2 = processing.runandload('gdalogr:cliprasterbymasklayer',
                                                  bohLayer1,  # INPUT <ParameterRaster>
                                                  boundary,  # MASK <ParameterVector>
                                                  "-9999",  # NO_DATA <ParameterString>
                                                  False,  # ALPHA_BAND <ParameterBoolean>
                                                  False,  # CROP_TO_CUTLINE <ParameterBoolean>
                                                  False,  # KEEP_RESOLUTION <ParameterBoolean>
                                                  5,  # RTYPE <ParameterSelection>
                                                  4,  # COMPRESS <ParameterSelection>
                                                  1,  # JPEGCOMPRESSION <ParameterNumber>
                                                  6,  # ZLEVEL <ParameterNumber>
                                                  1,  # PREDICTOR <ParameterNumber>
                                                  False,  # TILED <ParameterBoolean>
                                                  2,  # BIGTIFF <ParameterSelection>
                                                  False,  # TFW <ParameterBoolean>
                                                  "",  # EXTRA <ParameterString>
                                                  selectedOutput + '/clip_dem.tif')  # OUTPUT <OutputRaster>

            bohLayer5 = QgsRasterLayer(selectedOutput + '/clip_dem.tif', "DEM-clipped")
            boh5 = QgsRasterCalculatorEntry()
            boh5.ref = 'boh5@1'
            boh5.raster = bohLayer5
            boh5.bandNumber = 1
            entries.append(boh5)

            ## GDAL algorithm for slope
            processing.runalg('gdalogr:slope', bohLayer5, 1, False, True, True, 111120,
                              selectedOutput + '/slope(percent).tif')

            bohLayer6 = QgsRasterLayer(selectedOutput + '/slope(percent).tif', "slope(percent)")
            QgsMapLayerRegistry.instance().addMapLayer(bohLayer6)
            boh6 = QgsRasterCalculatorEntry()
            boh6.ref = 'boh6@1'
            boh6.raster = bohLayer6
            boh6.bandNumber = 1
            entries.append(boh6)


            # Process calculation with input extent and resolution
            calc = QgsRasterCalculator('(boh4@1 * boh6@1) *' + km_value, selectedOutput + '/soil_risk.tif', 'GTiff',
                                       bohLayer6.extent(), bohLayer6.width(), bohLayer6.height(), entries)

            calc.processCalculation()
            bohLayer4 = QgsRasterLayer(selectedOutput + '/soil_risk.tif', "Soil_Risk")
            QgsMapLayerRegistry.instance().addMapLayer(bohLayer4)





