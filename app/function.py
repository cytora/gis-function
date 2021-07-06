
import json
import os
from mangum import Mangum

from api import app


def handler(event, context):
    debug = os.getenv('DEBUG', '')
    if debug.lower() == 'true':
        evt = json.dumps(event)
        print(f'{evt}')
    if event.get("some-key"):
        # Do something or return, etc.
        return

    asgi_handler = Mangum(app)
    response = asgi_handler(event, context) # Call the instance with the event arguments
    return response
