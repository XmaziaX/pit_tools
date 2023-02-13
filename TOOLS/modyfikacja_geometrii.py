# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PitTools
                                 A QGIS plugin
 Plugin ułątwiający pracę z danymi UEK PIT.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-02-06
        copyright            : (C) 2023 by Tomasz Mazuga
        email                : tmazuga@gmail.com
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

__author__ = 'Tomasz Mazuga'
__date__ = '2023-02-06'
__copyright__ = '(C) 2023 by Tomasz Mazuga'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink, QgsGeometry, QgsMessageLog)
from qgis.PyQt.QtGui import QIcon, QColor
import os
import inspect
from .funkcje import *


class ModyfikacjaGeometrii(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_WEZLY = 'INPUT_WEZLY'
    INPUT_WEZLY_OBCE = 'INPUT_WEZLY_OBCE'
    INPUT_PUNKTY_LACZENIA = 'INPUT_PUNKTY_LACZENIA'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_WEZLY,
                self.tr('Warstwa  węzłów WW [punktowa]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('wezly')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_WEZLY_OBCE,
                self.tr('Warstwa  węzłów obcych WO [punktowa]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('wezly_obce')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_PUNKTY_LACZENIA,
                self.tr('Warstwa  punktów łączenia kabla [punktowa]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('punkty_laczenia_kabla')
            )
            )



    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source_pkt_ww = self.parameterAsSource(parameters, self.INPUT_WEZLY, context)
        source_pkt_wo = self.parameterAsSource(parameters, self.INPUT_WEZLY_OBCE, context)
        source_pkt_lk = self.parameterAsSource(parameters, self.INPUT_PUNKTY_LACZENIA, context)


        layer_ww = layer_by_part_of_name('wezly')
        layer_ww_objects = [[x['we01_id_wezla'], x.geometry()] for x in layer_ww.getFeatures() if
                            x.geometry().isEmpty() is False]


        # uzupelnianie geom dla interfejsy
        layer = layer_by_part_of_name('interfejsy')
        for features in layer.getFeatures():
            for wezel in layer_ww_objects:
                if features['node_name'] == wezel[0] and features['flag'] == '1':
                    layer.dataProvider().changeGeometryValues({features.id(): wezel[1]})
        layer.commitChanges()

        # uzupelnianie geom dla zasiegi_radiowe
        layer = layer_by_part_of_name('zasiegi_radiowe')
        for features in layer.getFeatures():
            for wezel in layer_ww_objects:
                if features['node_name'] == wezel[0] and features['flag'] == '1':
                    layer.dataProvider().changeGeometryValues({features.id(): wezel[1]})
        layer.commitChanges()

        # uzupelniaine linie kablowe
        layer_pl = layer_by_part_of_name('punkty_laczenia_kabla')
        layer_pl_objects = [[x['name'], x.geometry()] for x in layer_pl.getFeatures() if x.geometry().isNull() is False]
        layer_w = layer_by_part_of_name('wezly')
        layer_w_objects = [[x['we01_id_wezla'], x.geometry()] for x in layer_w.getFeatures() if
                           x.geometry().isNull() is False]
        layer_wo = layer_by_part_of_name('wezly_obce')
        layer_wo_objects = [[x['name'], x.geometry()] for x in layer_wo.getFeatures() if x.geometry().isNull() is False]
        layer_pl_w_wo_objects = layer_pl_objects + layer_w_objects + layer_wo_objects

        layer = layer_by_part_of_name('linie_kablowe')
        for features in layer.getFeatures():
            for punkt_p in layer_pl_w_wo_objects:
                if features['lk02_id_punktu_poczatkowego'] == punkt_p[0]:
                    point_start = punkt_p[1]
                    for punkt_k in layer_pl_w_wo_objects:
                        if features['lk04_id_punktu_koncowego'] == punkt_k[0]:
                            point_end = punkt_k[1]
                            geom = QgsGeometry.fromPolyline([point_start.get(), point_end.get()])
                            layer.dataProvider().changeGeometryValues({features.id(): geom})
                        else:
                            pass
                else:
                    pass
        layer.commitChanges()

        # budowa geometrii polaczenia
        layer = layer_by_part_of_name('polaczenia')
        for features in layer.getFeatures():
            for punkt_p in layer_pl_w_wo_objects:
                if features['node_start_name'] == punkt_p[0]:
                    point_start = punkt_p[1]
                    for punkt_k in layer_pl_w_wo_objects:
                        if features['node_end_name'] == punkt_k[0]:
                            point_end = punkt_k[1]
                            geom = QgsGeometry.fromPolyline([point_start.get(), point_end.get()])
                            layer.dataProvider().changeGeometryValues({features.id(): geom})
                        else:
                            pass
                else:
                    pass
        layer.commitChanges()

        # budowa geometri linii bezprzewodowych
        layer = layer_by_part_of_name('linie_bezprzewodowe')
        for features in layer.getFeatures():
            for punkt_p in layer_ww_objects:
                if features['lb02_id_punktu_poczatkowego'] == punkt_p[0]:
                    point_start = punkt_p[1]
                    for punkt_k in layer_ww_objects:
                        if features['lb03_id_punktu_koncowego'] == punkt_k[0]:
                            point_end = punkt_k[1]
                            geom = QgsGeometry.fromPolyline([point_start.get(), point_end.get()])
                            layer.dataProvider().changeGeometryValues({features.id(): geom})
                        else:
                            pass
                else:
                    pass
        layer.commitChanges()

        QgsMessageLog.logMessage(f'GOTOWE')
        return {}


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '3. Aktualizacja danych geometrycznych dla geokodowanych obiektów.'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Tools'

    def shortHelpString(self):
        """ Returns a localised short helper string for the algorithm. This string
            should provide a basic description about what the algorithm does and the
            parameters and outputs associated with it.."""
        return self.tr(("""
             Algorytm aktualizuje geometrię po geokodowaniu .
             
             PARAMETRY
             Brak - zaczytują się automatycznie.
             
             Aktualizuje geometrię w oparciu o zgeokodowane współrzędne.
             Aktualizowane są warstwy:
             - polaczenia
             - linie bezprzewodowe
             - linie kablowe
             -zasiegi_radiowe 
             - interfejsy
             
             WCZYTANE DO PROJEKTU WARSTWY TO WARSTWY TYPU MEMORY -ZNIKNĄ PO ZAMKNIĘCIU PROGRAMU.
             JEŚLI CHCESZ JE ZACHOWAĆ - UŻYJ ALGORYTMU Pakietuj warstwy do GeoPackage
                          
             """))

    def shortDescription(self):
        """
        Returns an optional translated short description of the algorithm. This should be at most
            a single sentence, e.g. “Converts 2D features to 3D by sampling a DEM raster.
            """
        return self.tr(" Algorytm aktualizuje geometrię po geokodowaniu ")

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(cmd_folder, 'icon_modyfikacja_geometrii.png'))
        return icon


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ModyfikacjaGeometrii()
