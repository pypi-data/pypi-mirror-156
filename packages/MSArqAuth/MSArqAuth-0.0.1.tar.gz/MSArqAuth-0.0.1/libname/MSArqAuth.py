from datetime import datetime, timedelta
import json
import jwt
import requests
from sqlalchemy import null
import xmltodict
import base64
import uuid
from xml.dom import minidom
import urllib
from os import getenv
from os.path import exists

def create_token(data: dict):
    time = datetime.utcnow() + timedelta(minutes=int(getenv("LIFETIMETOKEN")))
    token = jwt.encode(payload={**data, "exp": time}, key=getenv("SECRET"), algorithm="HS256")
    return token.encode("UTF-8")

def validate_token(token,resp = null, output = False):
    try:
        if output:
            _obj = jwt.decode(token, key=getenv("SECRET"), algorithms="HS256")
            return json.dumps(_obj)
        resp.status_code = 200
        resp.content_type = "application/json"
        _obj = jwt.decode(token, key=getenv("SECRET"),algorithms="HS256")
        resp.set_data(json.dumps(_obj))
    except jwt.exceptions.DecodeError:
        if output:
            response = json.dumps({"message":"Invalid Token"})
            return response
        resp.status_code = 401
        resp.content_type = "application/json"
        resp.set_data(json.dumps({"message":"Invalid Token"}))
    except jwt.exceptions.ExpiredSignatureError:
        if output:
            response = json.dumps({"message":"Token Expired"})
            return response
        resp.status_code = 400
        resp.content_type = "application/json"
        resp.set_data(json.dumps({"message":"Token Expired"}))

def createMetadata():
    url = getenv("SAMLMETADATAPATH")
    response = requests.get(url)
    with open("metadata.xml", 'wb') as file:
        file.write(response.content)

def getMetadata():
    if(not exists("metadata.xml")):
        createMetadata()
    with open("metadata.xml") as file:
        data = xmltodict.parse(file.read())
        entityID = data["md:EntityDescriptor"]["@entityID"]
        cert = data["md:EntityDescriptor"]["md:IDPSSODescriptor"]["md:KeyDescriptor"]["ds:KeyInfo"]["ds:X509Data"]["ds:X509Certificate"]
        sso = data["md:EntityDescriptor"]["md:IDPSSODescriptor"]["md:SingleSignOnService"][0]["@Location"]
        return [entityID, cert, sso]

def ResponseSSO(certificate,resp, responseString):
    str = base64.b64decode(responseString)
    identity = { "nameID" : "", "attributes" : [] }
    doc = minidom.parseString(str.decode('utf-8'))
    identity["nameID"] = doc.getElementsByTagName('saml2:NameID')[0].firstChild.data
    responseTo = doc.getElementsByTagName('saml2p:Response')[0]
    attrResponseTo =  base64.b64decode(responseTo.getAttribute('InResponseTo'))
    nodesAttr = doc.getElementsByTagName('saml2:Attribute')
    for item in nodesAttr:
        name = item.getAttribute('Name')
        value = item.getElementsByTagName('saml2:AttributeValue')[0].firstChild
        identity["attributes"].append({ "name" : name, "value" : value.data if value != None else '' })
    token = create_token(data=identity)
    resp.data =  json.dumps(token.decode("UTF-8"))
    resp.content_type = "application/json"
    resp.status_code = 200

def RedirectSAML(request, resp, issuer, samlEndPoint):
    getMetadata()
    _id = str(uuid.uuid4())
    _issue_instant = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    _assertionConsumerServiceUrl = request.host_url
    dom = minidom.parseString(
            str("<samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" {} {} {} {} {}></samlp:AuthnRequest>").
            format("ID=\"%s\"" % _id,"Version=\"2.0\"","IssueInstant=\"%s\"" % _issue_instant,"ProtocolBinding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST\"",
            "AssertionConsumerServiceURL=\"%s\"" % _assertionConsumerServiceUrl))
    root = dom.getElementsByTagName('samlp:AuthnRequest')[0]

    doomIssuer = minidom.parseString("<saml:Issuer xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\">%s</saml:Issuer>" % issuer)
    nodeIssuer = doomIssuer.getElementsByTagName('saml:Issuer')[0]
    root.appendChild(nodeIssuer)
    doomPolicy = minidom.parseString("<samlp:NameIDPolicy xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\"></samlp:NameIDPolicy>")
    nodePolicy = doomPolicy.getElementsByTagName('samlp:NameIDPolicy')[0]
    nodePolicy.setAttribute("Format","urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified")
    nodePolicy.setAttribute("AllowCreate", "true")
    root.appendChild(nodePolicy)

    strXML = str(root.toxml()).encode('utf-8')
    encodeXML = base64.b64encode(strXML)
    strEncode = encodeXML.decode('utf-8')

    queryStringSeparator = "?" if str(samlEndPoint).find("?") == -1 else "&"

    url = samlEndPoint + queryStringSeparator + "SAMLRequest=" + urllib.parse.quote(strEncode, safe='')
    resp.location = url
    resp.status_code = 500

def SSO(request, resp, newTokenGenerated = False):
    token = getHeaderAuth(request) if newTokenGenerated == False else ""    
    if(token != ""):
        validate_token(token, resp)
        return
    metadata = getMetadata()
    if(request.method == "POST" and request.form["SAMLResponse"] != null):
        ResponseSSO(metadata[1],resp, request.form["SAMLResponse"])
    else:
        RedirectSAML(request, resp, metadata[0],metadata[2])

def getHeaderAuth(request):
    _token = ""
    try:
        _token = request.headers['Authorization'].split(" ")[1]
    except:
        _token = ""
    if(_token == ""):
        try:
            _token = request.cookies["Authorization"]
        except:
            _token = ""
    return _token
