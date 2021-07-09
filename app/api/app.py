#from typing import Optional
import time
import psycopg2
#from psycopg2 import Error
#import ast
#import json
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from datetime import datetime
try:
    from .v1.settings import APP_PORT
    from .settings import VERSION, VERSION_DATE
    from .v1.settings import POSTGRESQL_DB_PORT, POSTGRESQL_DB_NAME, POSTGRESQL_DB_USER
    from .v1.settings import  POSTGRESQL_DB_PASSWORD, POSTGRESQL_DB_HOST
except Exception as ex:
    print(ex)
    from v1.settings import APP_PORT
    from v1.settings import POSTGRESQL_DB_PORT, POSTGRESQL_DB_NAME, POSTGRESQL_DB_USER
    from v1.settings import POSTGRESQL_DB_PASSWORD, POSTGRESQL_DB_HOST
    from settings import VERSION, VERSION_DATE

import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


cytora_app = Flask(__name__)  # , title='Cytora GeoSpatial Functions', description='Cytora powered GeoSpatial Functions powered by AWS, PostGIS, AirFlow, etc.')
cytora_app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI=os.getenv('GIS_DB_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(cytora_app)

API_VERSION = 'v1'

@cytora_app.route("/", methods=['GET'])
def get_service():
    return {
        'type': 'Lambda Function',
        'name': 'Cytora GIS Functions',
        'version': VERSION,
        'version_date': VERSION_DATE,
        'current_time': f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}",
        'sys_cpu_count': f'{os.cpu_count()}',
        'sys_os_uname': f'{os.uname()}'
    }


@cytora_app.route(f"/{API_VERSION}/check", methods=['GET'])
def get_check():
    return {'Cytora GeoSpatial Functions': 'Todor Lubenov and Liuben Siarov'}


@cytora_app.route(f"/{API_VERSION}/health_check", methods=['GET'])
def get_health_check():
    return {
        'current_time': f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}",
        'type': 'Lambda Function',
        'name': 'Cytora GIS Functions',
        'version': VERSION,
        'version_date': VERSION_DATE
    }


@cytora_app.route(f"/{API_VERSION}/discovery/layers", methods=['GET'])
def get_discovery():
    '''
    purpose: function discover available GeoSpatial Layers/Tables for query/search.
    get all tables with GEOM column in public Schema and respond back with object as follows:

    {
        "layers": [
            {
                "gis_layer": "geo_uk_haz_t100_03",
                "srid": 4326,
                "count": 1355
            },
            {
                "gis_layer": "geo_uk_haz_t10_03",
                "srid": 4326,
                "count": 12586
            },
            {
                "gis_layer": "geo_uk_haz_t5_03",
                "srid": 4326,
                "count": 24585
            }
        ],
        "exec_time_seconds": "2.403485804"
    }
    SRID stands for Spatial Reference ID. 4326 => WGS84, 27770 => UK GRID, ...
    COUNT presents number of objects/rows in given table/layer
    '''

    sql = '''
    select
        table_name as gis_layer
    from information_schema.columns
    where table_schema not in ('information_schema', 'pg_catalog') and column_name = 'geom' and table_schema = 'public'
    order by 
        table_schema, 
        table_name,
        ordinal_position;
    '''
    start = time.perf_counter()
    try:
        res = db.engine.execute(text(sql))
        results_as_dict = res.mappings().all()
        oo = []
        for el in results_as_dict:
            e = dict(el)
            gis_layer = el['gis_layer']

            count_sql = f'''
            SELECT reltuples::bigint as count
            FROM pg_catalog.pg_class
            WHERE relname = '{gis_layer}';'''
            r = db.engine.execute(text(count_sql))
            rd = r.mappings().all()
            cnt_for_layer = rd[0]['count']
            e['row_counts'] = cnt_for_layer

            #srid_sql = f'''SELECT Find_SRID('public', '{gis_layer}', 'geom');'''
            #print(srid_sql)
            #r = db.engine.execute(text(srid_sql))
            #srd = r.mappings().all()
            #e['srid'] = srd[0]

            geom_type = f'''SELECT count(1), ST_GeometryType(geom) as geom_type
                            from {gis_layer}
                            group by ST_GeometryType(geom);'''
            if cnt_for_layer > 10000:
                geom_type = f'''SELECT count(1), ST_GeometryType(geom) as geom_type
                                from {gis_layer}
                                group by ST_GeometryType(geom);'''
            #r = db.engine.execute(text(geom_type))
            #geom_typ = r.mappings().all()
            #print(geom_typ)
            #e['geometry'] = geom_typ[0]
            oo.append(e)

            #ext_sql = f'''SELECT ST_AsGeoJSON(ST_Extent(geom)) as extent FROM {el['gis_layer']};'''
            #ext = select_query_dict(con, ext_sql)
            #d = ast.literal_eval(ext[0]['extent'])
            #el['extent'] = d
        t = time.perf_counter() - start
        obj = {'layers': oo, 'exec_time_seconds': f'{t:.3f}'}
        return obj
    except Exception as ex:
        t = time.perf_counter() - start
        return {'error': str(ex), 'exec_time_seconds': f'{t:.3f}'}


@cytora_app.route(f"/{API_VERSION}/intersect", methods=['GET'])
def get_intersection():# latitude: float, longitude: float, layer: str):
    '''
    purpose: Find Intersection/drill down between caller provided lat, lon and feature layer name
    example

    request URI => http://.../v1/intersect?latitude=52.71&longitude=-1.82&layer=geo_uk_haz_t10_03

    response =>
    {
        "request": {
            "lat": 52.71,
            "lon": -1.82,
            "layer": "geo_uk_haz_t10_03"
        },
        "response": [
            {
                "id": 2558,
                "t10_id": "10_1_2558",
                "country": "Great Britain",
                "area_km2": 19
            }
        ],
        "exec_time_seconds": "0.677"
    }
    '''

    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    layer = request.args.get('layer')

    sql = f'''
    SELECT
    -- ST_AsGeoJSON(geom) as g,
    *
    FROM {layer}
    WHERE ST_Intersects(geom, 'SRID=4326;POINT({longitude} {latitude})');
    '''
    start = time.perf_counter()
    try:
        r = db.engine.execute(text(sql))
        res = r.mappings().all()
        res_arr = []

        #geometry = None
        for e in res:
            el = dict(e)
            #geometry = el['g']
            del el['geom']
            #del el['g']
            res_arr.append(el)

        t = time.perf_counter() - start
        obj = {
            'request': {
                'lat': latitude,
                'lon': longitude,
                'layer': layer},
            'response': res_arr,
            'exec_time_seconds': f'{t:.3f}'
        }
        #obj['response'].append(ast.literal_eval(geometry))
        return obj
    except Exception as ex:
        t = time.perf_counter() - start
        return {'error': str(ex), 'exec_time_seconds': f'{t:.3f}'}


if __name__ == '__main__':
    if os.getenv('DEBUG') and os.getenv('DEBUG').lower() == 'true':
        cytora_app.run()
