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
import pydocumentdb.errors as errors
from datetime import datetime
from flask import render_template
from flask import request
from flask_basicauth import BasicAuth
from BitWebAdmin import app

#app.config['BASIC_AUTH_USERNAME'] = 'wherebit'
#app.config['BASIC_AUTH_PASSWORD'] = 'simon'
#app.config['BASIC_AUTH_FORCE'] = True

#basic_auth = BasicAuth(app)

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

@app.route('/confirmrego', methods=['GET'])
def confirmrego():
    
    user = request.args.get('user')
    response = ""

    if user:

        client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

        try:
        
            # Try and find the user registration for the user
            doc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION + '/docs/' + user)

            # mark as confirmed so user can participate in the comp
            doc['confirmed'] = "true"
            client.ReplaceDocument(doc['_self'], doc)

            response = "OK"

        except errors.DocumentDBError as e:
            if e.status_code == 404:
                response = "could not find user"
            else:
                response = "unknown Cosmos error"
    else:
        response = "missing argument"

    return response

@app.route('/gameadmin', methods=['GET', 'POST'])
def gameadmin(): 
    form = GameAdminForm()

    # Create a model to pass to results.html
    class GameAdminObject:
        game_locale = ""
        game_round = 0
        person_group_id = ""

    admin_form_object = GameAdminObject()

    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

    doc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.GAME_CONFIG_COSMOSDB_COLLECTION + '/docs/' + config_cosmos.GAME_CONFIG_COSMOSDB_DOCUMENT)

    if form.validate_on_submit(): # is user submitted vote  
         
        doc['activeevent'] = form.event_location.data
        doc['persongroupid'] = form.person_group.data
        doc['activetier'] = form.game_round.data
        replaced_document = client.ReplaceDocument(doc['_self'], doc)

        #admin_form_object.game_locale = replaced_document['activeevent']
        #admin_form_object.game_round = replaced_document['activetier']
        #admin_form_object.person_group_id = replaced_document['persongroupid']

        return render_template(
            'saved.html', 
            year=datetime.now().year)
    
    else :
    
        # load existing values into the form

        form.event_location.data = doc['activeevent']
        form.person_group.data = doc['persongroupid']
        form.game_round.data = doc['activetier']

        admin_form_object.game_locale = doc['activeevent']
        admin_form_object.game_round = doc['activetier']
        admin_form_object.person_group_id = doc['persongroupid']
                
        return render_template(
            'gameadmin.html', 
            year=datetime.now().year,
		    admin_form_object = admin_form_object,
		    form = form)