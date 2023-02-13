# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PitTools
                                 A QGIS plugin
 Plugin ułatwiający pracę z danymi UEK PIT.
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
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsGeometry,
                       QgsPoint, QgsProcessingParameterCrs, QgsMessageLog
                        )
from qgis.PyQt.QtGui import QIcon, QColor
from .funkcje import *
import os
import inspect
import csv


class ImportDanych(QgsProcessingAlgorithm):
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

    INPUT_CSV = 'INPUT_CSV'
    CRS = 'CRS'
    FOLDER_PATH = 'FOLDER_PATH'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_CSV,
                description=self.tr('Wskaż plik CSV z danymi z SIIS [.csv]'),
                fileFilter="csv(*.csv)"
            ))

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.FOLDER_PATH,
                description=self.tr('Wskaż folder wynikowy, gdzie będzie zapisany plik GPKG'),
                behavior=QgsProcessingParameterFile.Folder
            ))

        self.addParameter(
            QgsProcessingParameterCrs(
                name=self.CRS,
                description=self.tr('Wybierz odwzorowanie (domyślnie układ 1992 EPSG:2180)'), defaultValue='EPSG:2180'
            ))



    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        crs_layer = self.parameterAsCrs(
            parameters,
            self.CRS,
            context)

        gpkg_path = self.parameterAsFile(
            parameters,
            self.FOLDER_PATH,
            context)

        file_csv_path = self.parameterAsFile(
            parameters,
            self.INPUT_CSV,
            context)

        QgsProject.instance().setCrs(crs_layer)
        gpkg_path = os.path.join( gpkg_path, (os.path.basename(file_csv_path).replace('csv', 'gpkg')))


        # tworzenie seq
        id_ww, id_z, id_po, id_i, id_lk, id_k, id_dp, id_ps, id_wo, id_lb, id_p, id_zs, id_u, id_pl = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        # tworzenie list_ob
        feat_ww = []
        feat_z = []
        feat_po = []
        feat_i = []
        feat_lk = []
        feat_k = []
        feat_dp = []
        feat_ps = []
        feat_wo = []
        feat_lb = []
        feat_p = []
        feat_zs = []
        feat_u = []
        feat_pl = []



        # atrybuty klas
        WW = ['id', 'we01_id_wezla', 'we02_tytul_do_wezla', 'owner_name', 'collocation_name', 'voivodeship_name',
              'county_name', 'municipality_name', 'we04_terc', 'city_name', 'we05_simc', 'street_name', 'we06_ulic',
              'we07_nr_porzadkowy', 'postal_code', 'we08_szerokosc', 'we09_dlugosc', 'object_type',
              'surface_availability', 'antenna_availability', 'ue_subsidy', 'project_name', 'implementation_status',
              'flag']
        Z = ['id', 'name', 'node_name', 'nodeinterface_name', 'licenced_range', 'radio_permit_no', 'sector_azimuth',
             'sector_width', 'antenna_height', 'sector_radius', 'max_transfer', 'project_name', 'implementation_status',
             'flag']
        PO = ['id', 'name', 'foreign_name', 'nip', 'regon', 'entity_no', 'voivodeship_name', 'county_name',
              'municipality_name', 'terc', 'city_name', 'sym', 'street_name', 'sym_ul', 'house_no', 'postal_code',
              'project_name', 'flag']
        I = ['id', 'name', 'node_name', 'backbone_layer', 'distribution_layer', 'access_layer', 'transmission_medium',
             'radio_frequency', 'technology', 'bandwidth', 'bandwidth_uplink', 'no_of_all', 'no_of_used', 'no_of_free',
             'sharing', 'project_name', 'implementation_status', 'flag']
        LK = ['id', 'lk01_id_lk', 'infrastructure_ownership', 'foreign_entity_name', 'element_start_type',
              'lk02_id_punktu_poczatkowego', 'element_end_type', 'lk04_id_punktu_koncowego', 'lk05_medium_transmisyjne',
              'fiber_type', 'lk07_liczba_wlokien', 'lk08_liczba_wlokien_wykorzystywanych', 'eu_funded',
              'passive_infrastructure_availability', 'passive_infrastructure_type', 'possibility_of_sharing',
              'shared_fibers_number', 'possibility_capacity_sharing', 'lk06_rodzaj_linii_kablowej', 'length',
              'lk11_numery_projektow_publ', 'implementation_status', 'flag']
        PL = ['id', 'name', 'voivodeship_name', 'county_name', 'municipality_name', 'terc', 'city_name', 'sym',
              'street_name', 'sym_ul', 'house_no', 'postal_code', 'latitude', 'longitude', 'object_type',
              'project_name', 'implementation_status', 'flag']
        WO = ['id', 'name', 'use_form', 'owner_name', 'voivodeship_name', 'county_name', 'municipality_name', 'terc',
              'city_name', 'sym', 'street_name', 'sym_ul', 'house_no', 'postal_code', 'latitude', 'longitude',
              'object_type', 'project_name', 'flag']
        ZS = ['id', 'name', 'ownership', 'usage', 'foreign_entity_name', 'node_name', 'voivodeship_name', 'county_name',
              'municipality_name', 'terc', 'city_name', 'sym', 'street_name', 'sym_ul', 'house_no', 'postal_code',
              'latitude', 'longitude', 'medium', 'technology', 'stationary_phone', 'stationary_voip', 'mobile_phone',
              'stationary_internet', 'mobile_internet', 'digital_tv', 'other_services', 'stationary_bandwidth',
              'mobile_bandwidth', 'project_name', 'implementation_status', 'flag']
        LB = ['id', 'lb01_id_lb', 'lb02_id_punktu_poczatkowego', 'lb03_id_punktu_koncowego', 'lb04_medium_transmisyjne',
              'lb05_nr_pozwolenia_radiowego', 'lb06_pasmo_radiowe', 'lb07_system_transmisyjny', 'lb08_przepustowosc',
              'lb09_mozliwosc_udostepniania', 'project_name', 'implementation_status', 'flag']
        P = ['id', 'name', 'ownership', 'element_owner_name', 'node_start_name', 'node_end_name', 'backbone_layer',
             'distribution_layer', 'access_layer', 'broadband_usage', 'voice_usage', 'other_usage', 'total_bandwidth',
             'broadband_bandwidth', 'project_name', 'implementation_status', 'flag']
        PS = ['id', 'name', 'own_node_name', 'foreign_node_name', 'own_node_interface_name', 'broadband_exchange',
              'voice_exchange', 'other_usage', 'bandwidth', 'broadband_transmission_bandwidth', 'project_name',
              'implementation_status', 'flag']
        DP = ['id', 'name', 'nip', 'regon', 'entity_no', 'rjst', 'krs', 'voivodeship_name', 'county_name',
              'municipality_name', 'terc', 'city_name', 'sym', 'street_name', 'sym_ul', 'house_no', 'postal_code',
              'homepage', 'email', 'agreement_nodes', 'agreement_cableconnections', 'agreement_contactpoints',
              'agreement_lines', 'agreement_nodeconnections', 'agreement_networkendpoints', 'person_first_name',
              'person_last_name', 'person_phone', 'person_fax', 'person_email', 'flag']

        # warstwy
        warstwy = [['podmiot_obcy', id_po, PO],
                   ['wezly', id_ww, WW],
                   ['interfejsy', id_i, I],
                   ['zasiegi_radiowe', id_z, Z], ['linie_kablowe', id_lk, LK], ['punkty_laczenia_kabla', id_pl, PL],
                   ['wezly_obce', id_wo, WO], ['zakonczenia_sieci', id_zs, ZS], ['polaczenia', id_p, P],
                   ['dane_podmiotu', id_dp, DP],
                   ['linie_bezprzewodowe', id_lb, LB]]

        # budowa QFields
        fields_PO = create_layer_fields(PO)
        fields_WW = create_layer_fields(WW)
        fields_I = create_layer_fields(I)
        fields_Z = create_layer_fields(Z)
        fields_LK = create_layer_fields(LK)
        fields_PL = create_layer_fields(PL)
        fields_WO = create_layer_fields(WO)
        fields_ZS = create_layer_fields(ZS)
        fields_P = create_layer_fields(P)
        fields_DP = create_layer_fields(DP)
        fields_LB = create_layer_fields(LB)
        fields_PS = create_layer_fields(PS)


        # przygotowanie konwersji 4326 -> 2180
        # sourceCrs = QgsCoordinateReferenceSystem(4326)
        # destCrs = QgsCoordinateReferenceSystem(2180)
        # tran = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())

        with open(file_csv_path, newline='\n') as csvfile:
            lines = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in lines:
                if row[0] == 'DP':
                    feat = create_object(row, DP, fields_DP)
                    id_dp += 1
                    feat['id'] = id_dp
                    feat['flag'] = 0
                    feat_dp.append(feat)
                elif row[0] == 'PO':
                    feat = create_object(row, PO, fields_PO)
                    id_po += 1
                    feat['id'] = id_po
                    feat['flag'] = 0
                    feat_po.append(feat)
                elif row[0] == 'PS':
                    feat = create_object(row, PS, fields_PS)
                    id_ps += 1
                    feat['id'] = id_ps
                    feat['flag'] = 0
                    feat_ps.append(feat)
                elif row[0] == 'WW':
                    feat = create_object(row, WW, fields_WW)
                    id_ww += 1
                    feat['id'] = id_ww
                    feat['flag'] = 0
                    if feat['we08_szerokosc'] == '' or feat['we09_dlugosc'] == '':
                        pass
                    else:
                        geom = QgsGeometry(QgsPoint(float(feat['we09_dlugosc']), float(feat['we08_szerokosc'])))
                        # bez dublowania def tran - z poziomu algorytmu nie konwertowaly sie dane
                        sourceCrs = QgsCoordinateReferenceSystem(4326)
                        destCrs = QgsCoordinateReferenceSystem(2180)
                        tran = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                        geom.transform(tran)
                        feat.setGeometry(geom)
                    feat_ww.append(feat)
                elif row[0] == 'WO':
                    feat = create_object(row, WO, fields_WO)
                    id_wo += 1
                    feat['id'] = id_wo
                    feat['flag'] = 0
                    if feat['longitude'] == '' or feat['latitude'] == '':
                        pass
                    else:
                        geom = QgsGeometry(QgsPoint(float(feat['longitude']), float(feat['latitude'])))
                        # bez dublowania def tran - z poziomu algorytmu nie konwertowaly sie dane
                        sourceCrs = QgsCoordinateReferenceSystem(4326)
                        destCrs = QgsCoordinateReferenceSystem(2180)
                        tran = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                        geom.transform(tran)
                        feat.setGeometry(geom)
                    feat_wo.append(feat)
                elif row[0] == 'I':
                    feat = create_object(row, I, fields_I)
                    id_i += 1
                    feat['id'] = id_i
                    feat['flag'] = 0
                    feat_i.append(feat)
                elif row[0] == 'Z':
                    feat = create_object(row, Z, fields_Z)
                    id_z += 1
                    feat['id'] = id_z
                    feat['flag'] = 0
                    feat_z.append(feat)
                elif row[0] == 'LK':
                    feat = create_object(row, LK, fields_LK)
                    id_lk += 1
                    feat['id'] = id_lk
                    feat['flag'] = 0
                    feat_lk.append(feat)
                elif row[0] == 'LB':
                    feat = create_object(row, LB, fields_LB)
                    id_lb += 1
                    feat['id'] = id_lb
                    feat['flag'] = 0
                    feat_lb.append(feat)
                elif row[0] == 'P':
                    feat = create_object(row, P, fields_P)
                    id_p += 1
                    feat['id'] = id_p
                    feat['flag'] = 0
                    feat_p.append(feat)
                elif row[0] == 'ZS':
                    feat = create_object(row, ZS, fields_ZS)
                    id_zs += 1
                    feat['id'] = id_zs
                    feat['flag'] = 0
                    if feat['longitude'] == '' or feat['latitude'] == '':
                        pass
                    else:
                        geom = (QgsGeometry(QgsPoint(float(feat['longitude']), float(feat['latitude']))))
                        # bez dublowania def tran - z poziomu algorytmu nie konwertowaly sie dane
                        sourceCrs = QgsCoordinateReferenceSystem(4326)
                        destCrs = QgsCoordinateReferenceSystem(2180)
                        tran = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                        geom.transform(tran)
                        feat.setGeometry(geom)
                    feat_zs.append(feat)
                elif row[0] == 'U':
                    pass
                elif row[0] == 'K':
                    id_k += 1
                elif row[0] == 'PL':
                    feat = create_object(row, PL, fields_PL)
                    id_pl += 1
                    feat['id'] = id_pl
                    feat['flag'] = 0
                    if feat['longitude'] == '' or feat['latitude'] == '':
                        pass
                    else:
                        geom = (QgsGeometry(QgsPoint(float(feat['longitude']), float(feat['latitude']))))
                        # bez dublowania def tran - z poziomu algorytmu nie konwertowaly sie dane
                        sourceCrs = QgsCoordinateReferenceSystem(4326)
                        destCrs = QgsCoordinateReferenceSystem(2180)
                        tran = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                        geom.transform(tran)
                        feat.setGeometry(geom)
                    feat_pl.append(feat)
                else:
                    pass
        # budowa zmiennych dla warstw
        layer_po = None
        layer_ww = None
        layer_i = None
        layer_z = None
        layer_lk = None
        layer_pl = None
        layer_wo = None
        layer_zs = None
        layer_p = None
        layer_dp = None
        layer_lb = None
        layer_ps = None

        # lista warstw z obiektami
        warstwy = [
            ['podmiot_obcy', feat_po, layer_po, id_po, 'None', fields_PO],
            ['wezly', feat_ww, layer_ww, id_ww, 'Point', fields_WW],
            ['interfejsy', feat_i, layer_i, id_i, 'Point', fields_I],
            ['zasiegi_radiowe', feat_z, layer_z, id_z, 'Point', fields_Z],
            ['linie_kablowe', feat_lk, layer_lk, id_lk, 'Linestring', fields_LK],
            ['punkty_laczenia_kabla', feat_pl, layer_pl, id_pl, 'Point', fields_PL],
            ['wezly_obce', feat_wo, layer_wo, id_wo, 'Point', fields_WO],
            ['zakonczenia_sieci', feat_zs, layer_zs, id_zs, 'Point', fields_ZS],
            ['linie_bezprzewodowe', feat_lb, layer_lb, id_lb, 'Linestring', fields_LB],
            ['polaczenia', feat_p, layer_p, id_p, 'Linestring', fields_P],
            ['punkty_styku', feat_ps, layer_ps, id_ps, 'Point', fields_PS],
            ['dane_podmiotu', feat_dp, layer_dp, id_dp, 'None', fields_DP]
        ]

        for war in warstwy:
            if war[3] > 0:
                # print(war[4], war[0], "memory")
                layer = QgsVectorLayer(war[4], war[0], "memory")
                crs = QgsCoordinateReferenceSystem(crs_layer)
                layer.setCrs(crs)
                pr = layer.dataProvider()
                pr.addAttributes(war[5])
                layer.updateFields()
                war[2] = layer
            else:
                pass

        # dodawanie obiektow do warstw
        for war in warstwy:
            if war[3] > 0:
                layer = war[2]
                (res, outFeats) = layer.dataProvider().addFeatures(war[1])
            else:
                pass
        for war in warstwy:
            if war[3] > 0:
                QgsProject.instance().addMapLayer(war[2])

        layer_ww = layer_by_part_of_name('wezly')
        layer_ww_objects = [[x['we01_id_wezla'], x.geometry()] for x in layer_ww.getFeatures() if
                            x.geometry().isNull() is False]

        # uzupelnianie geom dla interfejsy
        layer = layer_by_part_of_name('interfejsy')
        for features in layer.getFeatures():
            for wezel in layer_ww_objects:
                if features['node_name'] == wezel[0]:
                    layer.dataProvider().changeGeometryValues({features.id(): wezel[1]})

        # uzupelnianie geom dla zasiegi_radiowe
        layer = layer_by_part_of_name('zasiegi_radiowe')
        for features in layer.getFeatures():
            for wezel in layer_ww_objects:
                if features['node_name'] == wezel[0]:
                    layer.dataProvider().changeGeometryValues({features.id(): wezel[1]})

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



        for war in warstwy:
            if war[3] > 0:
                options = QgsVectorFileWriter.SaveVectorOptions()
                if not os.path.exists(gpkg_path):
                    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
                else:
                    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                options.EditionCapability = QgsVectorFileWriter.CanAddNewLayer
                options.layerName = war[0]
                QgsVectorFileWriter.writeAsVectorFormatV3(war[2], gpkg_path, QgsProject.instance().transformContext(),
                                                          options)


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
        return '1. Import danych z plików CSV.'

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
                
             PARAMETRY
             Należy wskazać plik CSV z SIIS.
             Folder gdzie ma być zapisana geopaczka z zaimportowanymi danymi.
             
             Są to dane z geometriami (takie jak w eksporcie z PIT) jak i rekordy bez geometrii.
             Narzędzie uzupełnia geometrię dla obiektów punktowych i liniowcyh  bazujących na innych obiektach z 
             geometrią (które były w SIIS).
             Każda tabela dostaje dodatkowy atrybut FLAG - służy do flagowania geometri powstałych z geokodowania.
             WCZYTANE DO PROJEKTU WARSTWY TO WARSTWY TYPU MEMORY -ZNIKNĄ PO ZAMKNIĘCIU PROGRAMU.
             JEŚLI CHCESZ JE ZACHOWAĆ - UŻYJ ALGORYTMU Pakietuj warstwy do GeoPackage
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
        icon = QIcon(os.path.join(cmd_folder, 'icon_import_danych.png'))
        return icon


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ImportDanych()
