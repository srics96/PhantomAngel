import json
import requests

from xml.dom.minidom import parseString
import xmlrpclib
import xml.etree.ElementTree as ET

import ast




import os.path
import sys

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


CLIENT_ACCESS_TOKEN = '75d2f175cd05473fbddba4d6475a49d8'
MESSAGE_SUBMISSION_URL = "https://api.api.ai/v1/query?v=20150910"
SESSION_ID = 1001
headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer b55df5347afe4002a39e94cd61c121c9'}

def call_api(session_id, query):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.session_id = session_id

    request.query = query

    response = request.getresponse()

    return response.read()

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def _find_key(somejson, key):
    def val(node):
        e = node.nextSibling
        while e and e.nodeType != e.ELEMENT_NODE:
            e = e.nextSibling
        return (e.getElementsByTagName('string')[0].firstChild.nodeValue if e 
                else None)
    foo_dom = parseString(xmlrpclib.dumps((json.loads(somejson),)))
    return [val(node) for node in foo_dom.getElementsByTagName('name') 
            if node.firstChild.nodeValue in key]


headers['Authorization'] = 'Bearer {0}'.format(CLIENT_ACCESS_TOKEN)
request_dict = {"query" : "Chandru will work on Backend", "sessionId" : SESSION_ID, "lang" : "en" } 
request_dict = json.dumps(request_dict)
response = requests.post(MESSAGE_SUBMISSION_URL, data=request_dict, headers=headers)
response = byteify(response.json())
print response
result_json =  response['result']
action_incomplete = result_json['actionIncomplete']
print action_incomplete