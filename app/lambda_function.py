
import json
import os
# from mangum import Mangum
from apig_wsgi import make_lambda_handler

from api import app

# lambda_handler = Mangum(app=app)

'''
def lambda_handler(event, context):
    debug = os.getenv('DEBUG', '')
    if debug.lower() == 'true':
        evt = json.dumps(event)
        print(f'{evt}')

    asgi_handler = Mangum(app)
    response = asgi_handler(event, context) # Call the instance with the event arguments
    return response
'''

lambda_handler = make_lambda_handler(app.wsgi_app)


def handler(event, context):
    debug = os.getenv("DEBUG", "")
    if debug.lower() == "true":
        evt = json.dumps(event)
        print(f'{evt}')
    return lambda_handler(event, context)
