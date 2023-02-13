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
                       QgsProcessingParameterFeatureSink, QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                       QgsGeometry, QgsMessageLog)
from qgis.PyQt.QtGui import QIcon, QColor
import os
import inspect
import requests
import time
from .funkcje import *


class DaneAdresowe(QgsProcessingAlgorithm):
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
        headers = {'Accept': 'application/json'}
        def _zlicz_obiekty_z_pusta_geom(layer: QgsVectorLayer)->int:
            ile_pustych = 0
            for x in layer.getFeatures():
                if x.geometry().isEmpty():
                    ile_pustych += 1
                else:
                    pass
            return ile_pustych

        source_pkt_ww = self.parameterAsSource(parameters, self.INPUT_WEZLY, context)
        source_pkt_wo = self.parameterAsSource(parameters, self.INPUT_WEZLY_OBCE, context)
        source_pkt_lk = self.parameterAsSource(parameters, self.INPUT_PUNKTY_LACZENIA, context)
        suma_ob = _zlicz_obiekty_z_pusta_geom(source_pkt_ww) + _zlicz_obiekty_z_pusta_geom(source_pkt_wo) + _zlicz_obiekty_z_pusta_geom(source_pkt_lk)
        QgsMessageLog.logMessage(f'suma_obiektow so geokodowania:  {suma_ob}')

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / suma_ob if suma_ob else 0
        obiekty = list(range(suma_ob))
        current = 0
        for feature in obiekty:
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

        sourceCrs = QgsCoordinateReferenceSystem(2180)
        destCrs = QgsCoordinateReferenceSystem(4326)
        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())

        # wezly
        layer_wezly = layer_by_part_of_name('wezly')
        wezly = list(layer_wezly.getFeatures())
        for feature in wezly:
            if feature.geometry().isEmpty():
                miasto = feature['city_name']
                ulica = feature['street_name']
                numer = feature['we07_nr_porzadkowy']
                kod = feature['postal_code']
                id = feature['id']
                if numer is False or numer == '0':
                    pass
                else:
                    if ulica == 'BRAK ULICY' or ulica is False:
                        zap = 'https://services.gugik.gov.pl/uug/?request=GetAddress&address=' + miasto + ',%20' + numer
                    else:
                        zap = 'https://services.gugik.gov.pl/uug/?request=GetAddress&address=' + miasto + ',%20' + ulica + '%20' + numer
                r = requests.get(zap, headers=headers)
                results_dict = r.json()
                if results_dict['results'] is None:
                    pass
                else:
                    if results_dict['returned objects'] == 1:
                        nr_adress = '1'
                    else:
                        for k, v in results_dict['results'].items():
                            if v['code'] == kod:
                                nr_adress = v['id']
                                break
                            else:
                                nr_adress = '0'
                    if int(nr_adress) >= 1:
                        wkt = results_dict['results'][str(nr_adress)]['geometry_wkt']
                        geom = QgsGeometry.fromWkt(wkt)
                        layer_wezly.dataProvider().changeGeometryValues({feature.id(): geom})
                        geom.transform(tr)
                        x = geom.get().x()
                        y = geom.get().y()
                        attrs = {15: f'{y:.5f}', 16: f'{x:.5f}', 23: f'1'}
                        layer_wezly.dataProvider().changeAttributeValues({feature.id(): attrs})
                        current += 1
                        layer_wezly.commitChanges()
                        feedback.setProgress(int(current * total))
                    # # time.sleep(1)
                    else:
                        pass
            else:
                pass

        # wezly_obce
        layer_wezly = layer_by_part_of_name('wezly_obce')
        wezly = list(layer_wezly.getFeatures())
        for feature in wezly:
            if feature.geometry().isEmpty():
                miasto = feature['city_name']
                ulica = feature['street_name']
                numer = feature['house_no']
                kod = feature['postal_code']
                id = feature['id']
                if numer is False or numer == '0':
                    pass
                else:
                    if ulica == 'BRAK ULICY' or ulica is False:
                        zap = 'https://services.gugik.gov.pl/uug/?request=GetAddress&address=' + miasto + ',%20' + numer
                    else:
                        zap = 'https://services.gugik.gov.pl/uug/?request=GetAddress&address=' + miasto + ',%20' + ulica + '%20' + numer
                r = requests.get(zap, headers=headers)
                results_dict = r.json()
                if results_dict['results'] is None:
                    pass
                else:
                    if results_dict['returned objects'] == 1:
                        nr_adress = '1'
                    else:
                        for k, v in results_dict['results'].items():
                            if v['code'] == kod:
                                nr_adress = v['id']
                                break
                            else:
                                nr_adress = '0'
                    if int(nr_adress) >= 1:
                        wkt = results_dict['results'][str(nr_adress)]['geometry_wkt']
                        geom = QgsGeometry.fromWkt(wkt)
                        layer_wezly.dataProvider().changeGeometryValues({feature.id(): geom})
                        geom.transform(tr)
                        x = geom.get().x()
                        y = geom.get().y()
                        attrs = {14: f'{y:.5f}', 15: f'{x:.5f}', 18: f'1'}
                        layer_wezly.dataProvider().changeAttributeValues({feature.id(): attrs})
                        layer_wezly.commitChanges()
                        feedback.setProgress(int(current * total))
                    # time.sleep(1)
                    else:
                        pass

            else:

                pass
        # punkty_laczenia_kabla
        layer_wezly = layer_by_part_of_name('punkty_laczenia_kabla')
        wezly = list(layer_wezly.getFeatures())
        for feature in wezly:
            if feature.geometry().isEmpty():
                miasto = feature['city_name']
                ulica = feature['street_name']
                numer = feature['house_no']
                kod = feature['postal_code']
                id = feature['id']
                if numer is False or numer == '0':
                    pass
                else:
                    if ulica == 'BRAK ULICY' or ulica is False:
                        zap = 'https://services.gugik.gov.pl/uug/?request=GetAddress&address=' + miasto + ',%20' + numer
                    else:
                        zap = 'https://services.gugik.gov.pl/uug/?request=GetAddress&address=' + miasto + ',%20' + ulica + '%20' + numer
                r = requests.get(zap, headers=headers)
                results_dict = r.json()
                if results_dict['results'] is None:
                    pass
                else:
                    if results_dict['returned objects'] == 1:
                        nr_adress = '1'
                    else:
                        for k, v in results_dict['results'].items():
                            if v['code'] == kod:
                                nr_adress = v['id']
                                break
                            else:
                                nr_adress = '0'
                    if int(nr_adress) >= 1:
                        wkt = results_dict['results'][str(nr_adress)]['geometry_wkt']
                        geom = QgsGeometry.fromWkt(wkt)
                        layer_wezly.dataProvider().changeGeometryValues({feature.id(): geom})
                        geom.transform(tr)
                        x = geom.get().x()
                        y = geom.get().y()
                        attrs = {12: f'{y:.5f}', 13: f'{x:.5f}', 17: f'1'}
                        layer_wezly.dataProvider().changeAttributeValues({feature.id(): attrs})
                        layer_wezly.commitChanges()
                        feedback.setProgress(int(current * total))
                    # # time.sleep(1)
                    else:
                        pass
            else:
                pass
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
        return '2. Aktualizacja danych adresowych.'

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
             Algorytm aktualizuje w projekcie bazę danych adresowych oraz ulic.
             
             PARAMETRY
             Brak - zaczytują się automatycznie.
             
             Pomijane są adresy bez numerów  lub z numerami równymi 0.
             Aktualizowana jest geometria.
             Wpisywane są  dł/szer w ukłądzie WGS84.
             Uzupełnione elementy otrzymują  wartość w atrybucie flag = 1 (inne domyślnie mają tam 0.
             
             NIE MODYFIKOWAŁEM KODÓW TERC SIMC ULIC (pominąłem, ale to można łatwo dodać)
             Uzupełniane są warstwy: wezły (WW), wezly_obce (WO)   , punkty_laczenia_kabla (PL)             
             """))

    def shortDescription(self):
        """
        Returns an optional translated short description of the algorithm. This should be at most
            a single sentence, e.g. “Converts 2D features to 3D by sampling a DEM raster.
            """
        return self.tr("Jakis opis.")

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(cmd_folder, 'icon_dane_adresowe.png'))
        return icon


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return DaneAdresowe()