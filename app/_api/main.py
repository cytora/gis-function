import os

from fastapi import FastAPI
from datetime import datetime
try:
    from .v1.routers import router
    from .v1.settings import APP_PORT
    from .settings import VERSION, VERSION_DATE
except Exception as ex:
    print(ex)
    from v1.routers import router
    from v1.settings import APP_PORT
    from settings import VERSION, VERSION_DATE

app = FastAPI(title='Cytora GeoSpatial Functions', description='Cytora powered GeoSpatial Functions powered by AWS, PostGIS, AirFlow, etc.')
app.include_router(router, prefix='/v1')


@app.get('/')
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

@app.get('/v1/check')
def read_root():
    return {'Cytora GeoSpatial Functions': 'Todor Lubenov and Liuben Siarov'}


@app.get('/v1/health_check')
def read_root():
    return {
        'current_time': f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}",
        'type': 'Lambda Function',
        'name': 'Cytora GIS Functions',
        'version': VERSION,
        'version_date': VERSION_DATE
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(APP_PORT))
