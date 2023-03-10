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
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsVectorFileWriter,
                       QgsProject,
                       QgsProcessingParameterEnum,
                       QgsMessageLog
                       )
from qgis.PyQt.QtGui import QIcon, QColor
import os
import inspect
from .funkcje import *
from .schematy_danych import CSV # SHP, CSV, KML, GML, GPKG, GEOJSON


class EksportPit(QgsProcessingAlgorithm):
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

    INPUT_BUDYNKI_KOLOKACJA = 'INPUT_BUDYNKI_KOLOKACJA'
    INPUT_PUNKTY_ELASTYCZNOSCI = 'INPUT_PUNKTY_ELASTYCZNOSCI'
    INPUT_STACJE_BAZOWE = 'INPUT_STACJE_BAZOWE'
    INPUT_USLUGI_WADRESACH = 'INPUT_USLUGI_WADRESACH'
    INPUT_WEZLY = 'INPUT_WEZLY'
    INPUT_LINIE_BEZPRZEWODOWE = 'INPUT_LINIE_BEZPRZEWODOWE'
    INPUT_LINIE_KABLOWE = 'INPUT_LINIE_KABLOWE'
    FOLDER_PATH = 'FOLDER_PATH'
    EXPORT_FORMAT = 'EXPORT_FORMAT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.FOLDER_PATH,
                description=self.tr('1. Wskaż folder wynikowy, gdzie będą utworzone pliki SHP'),
                behavior=QgsProcessingParameterFile.Folder
            ))

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.EXPORT_FORMAT,
                description=self.tr('2. Format eksportu danych'),
                options=['CSV'],
                allowMultiple=False,
                defaultValue='KML'))


        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_BUDYNKI_KOLOKACJA,
                self.tr('3 Warstwa z gpkg z budynkami kolokacji [punkty]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('budynki_kolokacj')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_PUNKTY_ELASTYCZNOSCI,
                self.tr('4 Warstwa z gpkg z punktami elastycznosci  [punkty]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('punkty_elastycznosci')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_STACJE_BAZOWE,
                self.tr('5 Warstwa z gpkg ze stacjami bazowymi  [punkty]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('stacje_bazowe')
            )
            )


        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_USLUGI_WADRESACH,
                self.tr('6 Warstwa z gpkg z usługami w adresach [punkty]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('uslugi_wadresach')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_WEZLY,
                self.tr('7 Warstwa z gpkg z węzłami [punkty]'),
                [QgsProcessing.TypeVectorPoint], defaultValue=layer_by_part_of_name('wezly')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LINIE_BEZPRZEWODOWE,
                self.tr('8 Warstwa z gpkg z liniami bezprzewodowymi [linie]'),
                [QgsProcessing.TypeVectorLine], defaultValue=layer_by_part_of_name('linie_bezprzewodowe')
            )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LINIE_KABLOWE,
                self.tr('9 Warstwa z gpkg z liniami kablowymi [linie]'),
                [QgsProcessing.TypeVectorLine], defaultValue=layer_by_part_of_name('liniekablowe')
            )
            )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        folder_path = self.parameterAsFile(
            parameters,
            self.FOLDER_PATH,
            context)

        export_type = self.parameterAsString(
            parameters,
            self.EXPORT_FORMAT,
            context)
        QgsMessageLog.logMessage(f'Typ exp  {export_type}')

        budynki_kolokacj = self.parameterAsVectorLayer(parameters,
            self.INPUT_BUDYNKI_KOLOKACJA,
            context)

        punkty_elastycznosci = self.parameterAsVectorLayer(parameters,
            self.INPUT_PUNKTY_ELASTYCZNOSCI,
            context)

        stacje_bazowe = self.parameterAsVectorLayer(parameters,
            self.INPUT_STACJE_BAZOWE,
            context)

        uslugi_wadresach = self.parameterAsVectorLayer(parameters,
            self.INPUT_USLUGI_WADRESACH,
            context)

        wezly = self.parameterAsVectorLayer(parameters,
            self.INPUT_WEZLY,
            context)

        linie_bezprzewodowe = self.parameterAsVectorLayer(parameters,
            self.INPUT_LINIE_BEZPRZEWODOWE,
            context)

        liniekablowe = self.parameterAsVectorLayer(parameters,
            self.INPUT_LINIE_KABLOWE,
            context)

        # słownik zawierający atrybuty, które ma zawierać SHP ekportowany
        # tworzenie folderu
        create_folder(folder_path)
        #TODO dodac spr czy warstwa w projekcie
        lista_warstw_do_exp = [budynki_kolokacj, punkty_elastycznosci, stacje_bazowe, uslugi_wadresach, wezly,
                              linie_bezprzewodowe,liniekablowe]
        for f in lista_warstw_do_exp:
            f = drop_attributes_outside_list(f, SHP[f.name()])
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.fileEncoding = "UTF-8"
            options.driverName = "ESRI Shapefile"
            options.includeZ = True
            QgsVectorFileWriter.writeAsVectorFormatV3(f, os.path.join(folder_path, f.name() + '.shp'),
                                                QgsProject.instance().transformContext(), options)

        return {}




    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '5. Eksport danych do SHP.'

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
             Algorytm aktualizuje układ współrzędych warstw projektowych geopaczki.               
             """))

    def shortDescription(self):
        """
        Returns an optional translated short description of the algorithm. This should be at most
            a single sentence, e.g. “Converts 2D features to 3D by sampling a DEM raster.
            """
        return self.tr("Algorytm aktualizuje układ współrzędych warstw projektowych geopaczki")

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(cmd_folder, 'icon_eksport_danych.png'))
        return icon


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return EksportPit()
