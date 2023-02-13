import os
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsVectorFileWriter,
                       QgsProject,
                       QgsVectorLayer, QgsFields, QgsField, QgsFeature
                       )

def layer_by_part_of_name(match_str: str) -> str:
    """Funkcja zwraca nazwę, której nazwa kończy się na wartość argumentu"""
    for layer in [layer.name() for layer in QgsProject.instance().mapLayers().values()]:
        if layer.endswith(match_str):
            layer = QgsProject.instance().mapLayersByName(layer)[0]
            return layer
        else:
            pass

def create_layer_fields(type: str) -> QgsFields:
    """funcja buduje QgsFields dla typu warstwy"""
    layer_name_fields = QgsFields()
    for atr in type:
        if atr == 'id':
            layer_name_fields.append(QgsField(atr, QVariant.Int, 'Integer', 0, 0))
        else:
            layer_name_fields.append(QgsField(atr, QVariant.String, 'String', 0))
    return layer_name_fields


def create_folder(path: str) -> None:
    """ Funkcja tworząca folder o ile nie istnieje"""
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        pass


def create_object(row: list, type: list, layer_fields: QgsFields) -> QgsFeature:
    feat = QgsFeature(layer_fields)
    atr = dict(zip(type, row))
    for key, value in atr.items():
        feat[key] = value
    return feat

