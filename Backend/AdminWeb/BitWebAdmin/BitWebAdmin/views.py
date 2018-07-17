"""
Routes and views for the flask application.
"""

import cognitive_face as CF
import face_config
from forms import GameAdminForm
from flask_wtf import Form
from wtforms import StringField
import config_cosmos
import pydocumentdb.document_client as document_client
from datetime import datetime
from flask import render_template
from flask_basicauth import BasicAuth
from BitWebAdmin import app


app.config['BASIC_AUTH_USERNAME'] = 'john'
app.config['BASIC_AUTH_PASSWORD'] = 'matrix'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/trainmodel', methods=['GET'])
def trainmodel(): 

    CF.Key.set(face_config.FACE_KEY)
    CF.BaseUrl.set(face_config.FACE_HOST)

    CF.person_group.train("swtestgroup01")

    return render_template(
        'trainmodel.html',
        title='Train Model',
        year=datetime.now().year,
        message='Training Model.'
    )

@app.route('/trainingstatus', methods=['GET'])
def trainingstatus():
    CF.Key.set(face_config.FACE_KEY)
    CF.BaseUrl.set(face_config.FACE_HOST)

    return CF.person_group.get_status("swtestgroup01")['status']

@app.route('/gameadmin', methods=['GET', 'POST'])
def gameadmin(): 
    form = GameAdminForm()
  
    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

    # Read databases and take first since id should not be duplicated.
    db = next((data for data in client.ReadDatabases() if data['id'] == config_cosmos.COSMOSDB_DATABASE))

    # Read collections and take first since id should not be duplicated.
    coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == config_cosmos.COSMOSDB_COLLECTION))

    # Read documents and take first since id should not be duplicated.
    doc = next((doc for doc in client.ReadDocuments(coll['_self']) if doc['id'] == config_cosmos.COSMOSDB_DOCUMENT))

    # Take the data from the deploy_preference and increment our database
    #doc[form.deploy_preference.data] = doc[form.deploy_preference.data] + 1
    #replaced_document = client.ReplaceDocument(doc['_self'], doc)

    # Create a model to pass to results.html
    class GameAdminObject:
        game_locale = ""
        game_round = 0

    admin_form_object = GameAdminObject()
    admin_form_object.game_locale = doc['activeevent']
    admin_form_object.game_round = doc['activetier']

    form.game_locale = doc['activeevent']
        
    return render_template(
        'gameadmin.html', 
        year=datetime.now().year,
		admin_form_object = admin_form_object,
		form = form)