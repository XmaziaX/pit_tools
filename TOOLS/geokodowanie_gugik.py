import requests
from qgis.core import QgsGeometry

def geokodowanie_adresu(miejscowosc: str, ulica: str, numer:str , kod:str ) -> QgsGeometry:
    headers = {'Accept': 'application/json'}
    if miejscowosc is False or miejscowosc == '':
        return QgsGeometry()
    elif numer is False or numer == '0' or numer == '':
        return QgsGeometry()
    elif ulica == 'BRAK ULICY' or ulica is False or ulica == '':
        zap = f'https://services.gugik.gov.pl/uug/?request=GetAddress&address={miejscowosc},%20{numer}'
    else:
        zap = f'https://services.gugik.gov.pl/uug/?request=GetAddress&address={miejscowosc},%20{ulica}%20{numer}'
    try:
        r = requests.get(zap, headers=headers)
        results_dict = r.json()
        if results_dict['results'] is None:
            return QgsGeometry()
        elif results_dict['returned objects'] == 1:
            nr_adress = 1
        else:
            for k, v in results_dict['results'].items():
                if v['code'] == kod:
                    nr_adress = v['id']
                    break
                else:
                    nr_adress = '0'
        if int(nr_adress) >= 1:
            wkt = results_dict['results'][str(nr_adress)]['geometry_wkt']
            return QgsGeometry.fromWkt(wkt)
        else:
            return QgsGeometry()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

