# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MultipleLayersEdit
                                 A QGIS plugin
 Add buttons to turn on edit mode, commit, undo, filter selected layers.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-04-09
        git sha              : $Format:%H$
        copyright            : (C) 2020 by djes
        email                : djes@free.fr
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
from PyQt5.QtCore import (  QSettings, 
                            QTranslator, 
                            qVersion, 
                            QCoreApplication,
                            QVariant)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.core import QgsProject, QgsLayerTreeLayer, QgsVectorLayer
from qgis.utils import iface
from qgis.gui import QgsQueryBuilder

# Initialize Qt resources from file resources.py
from .resources import *
import os.path

class MultipleLayersEdit:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'MultipleLayersEdit_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Multiple Layers Edit')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('MultipleLayersEdit', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/multiple_layers_edit/'

        # will be set False in run()
        self.first_start = True

        # own toolbar init
        self.toolbar = self.iface.addToolBar(self.tr(u'Multiple Layers Toolbar'))
        self.toolbar.setObjectName("My toolbar Plugin")

        self.action_edit        = QAction(QIcon(icon_path + 'multiple_layers_edit.png'), self.tr(u'Set edit mode for selected layers'), self.iface.mainWindow())
        self.action_commit      = QAction(QIcon(icon_path + 'multiple_layers_commit.png'), self.tr(u'Commit selected layers'), self.iface.mainWindow())
        self.action_undo        = QAction(QIcon(icon_path + 'multiple_layers_undo.png'), self.tr(u'Undo selected layers'), self.iface.mainWindow())
        self.action_filter      = QAction(QIcon(icon_path + 'multiple_layers_filter.png'), self.tr(u'Filter selected layers'), self.iface.mainWindow())
        self.action_clearfilter = QAction(QIcon(icon_path + 'multiple_layers_clearfilter.png'), self.tr(u'Clear selected layers filter'), self.iface.mainWindow())

        self.action_edit.triggered.connect(self.run_edit)
        self.action_commit.triggered.connect(self.run_commit)
        self.action_undo.triggered.connect(self.run_undo)        
        self.action_filter.triggered.connect(self.run_filter)
        self.action_clearfilter.triggered.connect(self.run_clearfilter)

        self.toolbar.addActions([self.action_edit, self.action_commit, self.action_undo, self.action_filter, self.action_clearfilter])

    def unload(self):
        del self.toolbar

    def run_edit(self):
        """Run method that performs the edit"""
          
        selectedLayers = iface.layerTreeView().selectedLayersRecursive()
        for layer in selectedLayers:
            layer.startEditing()
            layer.triggerRepaint()

    def run_commit(self):
        """Run method that performs the commit"""
          
        selectedLayers = iface.layerTreeView().selectedLayersRecursive()
        for layer in selectedLayers:
            layer.commitChanges()
            layer.triggerRepaint()

    def run_undo(self):
        """Run method that performs the undo"""
          
        selectedLayers = iface.layerTreeView().selectedLayersRecursive()
        for layer in selectedLayers:
            layer.rollBack()
            layer.triggerRepaint()

    def run_filter(self):
        """Run method that performs the filter"""
        
        #Retrieve selected layers (or group members)
        selectedLayers = iface.layerTreeView().selectedLayersRecursive()
        #Sadly, the layer order is not good, so will sort it by name
        sortedSelectedLayers = sorted(selectedLayers, key=lambda x: x.name())

        # To creates layer
        # layer = QgsVectorLayer("Point?crs=epsg:4326&index=yes",
        #                     "temporary_points", "memory")
        # QgsProject.instance().addMapLayer(layer)

        # Look up for the first valid layer
        for layer in sortedSelectedLayers:

            if layer and layer.isValid():
            
                #Fire up the query builder based on the first layer
                query_builder = QgsQueryBuilder(layer)
                #query_builder.setSql(u'"age" > 30')
                query_builder.accept()
                
                if query_builder.exec_(): #exec_ waits, show not
                
                    expression = query_builder.sql()

                    #Set filter for all selected layers
                    for layer in sortedSelectedLayers:
                        layer.setSubsetString(expression)
                        layer.triggerRepaint()
#                        print(layer)
#                        print(layer.id())
                    
                del(query_builder)
                del(layer)
                
                #exit loop
                break
        
        #No valid layer selected, quits
              
    def run_clearfilter(self):
        """Run method that performs the clear filter"""

        selectedLayers = iface.layerTreeView().selectedLayersRecursive()
        for layer in selectedLayers:
            layer.setSubsetString('')
            layer.triggerRepaint()