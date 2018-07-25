"""
Routes and views for the flask application.
"""

import random
import cognitive_face as CF
import face_config
from forms import GameAdminForm, ConfirmUserForm, FindUserForm
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired
from wtforms import BooleanField
import config_cosmos
import pydocumentdb
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
from datetime import datetime
from flask import render_template
from flask import request
from flask_basicauth import BasicAuth
from BitWebAdmin import app

from applicationinsights import TelemetryClient
tc = TelemetryClient(app.config['APPINSIGHTS_INSTRUMENTATIONKEY'])

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

@app.route('/findplayer')
def findplayer():

    form = FindUserForm()

    return render_template(
        'findplayer.html',
        title='Find Player',
        year=datetime.now().year,
        form = form
    )

@app.route('/confirmplayer', methods=['POST'])
def confirmplayer():
   
    form = ConfirmUserForm() 
    form.user_name = request.form['user_name']
    img_user = ""
    player_lookup_status = ""
    player_save_status = ""

    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

    if form.validate_on_submit():
    
        # Save the form details to Cosmos
        try:

            # Try and find the user registration for the player
            userDoc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION + '/docs/' + request.form['user_name'])

            # Update the registration to confirmed so player can play
            userDoc['confirmed'] = form.user_confirmed.data
            client.ReplaceDocument(userDoc['_self'], userDoc)

            player_save_status = "Saved OK"

        except errors.DocumentDBError as e:
            tc.track_exception()
            tc.flush()
                
            player_save_status = "Unknown error saving user (" + e.status_code + ")"

    else:

        # Try and find the user registration for the player and at least one valid Face API processed selfie

        try:
                    
            userDoc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION + '/docs/' + request.form['user_name'])

            # Set the checked state of the field based on true / false in Cosmos
            form.user_confirmed.checked = userDoc['confirmed']
           
        except errors.DocumentDBError as e:
            tc.track_exception()
            tc.flush()
            if e.status_code == 404:
                player_lookup_status = "Could not find user (404)"
            else:
                player_lookup_status = "Unknown error finding user (" + e.status_code + ")"

        try:

            # If we found the user go ahead and try and find a valid Face image for them
            if player_lookup_status == "":
                options = {} 
                options['maxItemCount'] = 1

                # Select image for user (may be multiple so we will take only 1). Ensure it's an image with a valid Face ID and not just a random image
                query = {
                        "query": "SELECT * FROM u WHERE u.userid=@userId AND u.faceid<>''",
                        "parameters" : [
                                { "name": "@userId", "value": request.form['user_name'] }
                            ]
                        }

                images = list(client.QueryDocuments('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_IMAGES_COSMOSDB_COLLECTION, query, options))
                img_user = images[0]['imgurl']
    
        except:
            tc.track_exception()
            tc.flush()

    return render_template(
        'confirmplayer.html',
        title='Confirm Player',
        year=datetime.now().year,
        form=form,
        playerlookup=player_lookup_status,
        playersave=player_save_status,
        imgurl=img_user
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

        try:
            
        # Select confirmed users that haven't been Bit before. Support groups of up to 1,000 players because that's the max for a standard Person Group in Face API.
            query = {
                    "query": "SELECT TOP 1000 * FROM u WHERE u.confirmed=true AND u.byteround=0",
                    }
            
            results = list(client.QueryDocuments('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION, query))

            # total available users 
            item_count = len(results)
            # select a random integer representing position in list to select
            user_to_select = random.randint(0,item_count-1)
            # select new Bit user from list - list consists of document ID
            new_bit_user = results[user_to_select]

            # Read the full Cosmos document for the user
            userDoc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION + '/docs/' + new_bit_user)

            # Set the round ID to be the currently selected round.
            #userDoc['byteround'] = form.game_round.data
            # Write document back to Cosmos
            #client.ReplaceDocument(userDoc['_self'], userDoc)
       
        except errors.DocumentDBError as e:

            tc.track_exception()
            tc.flush()

            if e.status_code == 404:
                print("Document doesn't exist")
            elif e.status_code == 400:
                # Can occur when we are trying to query on excluded paths
                print("Bad Request exception occured: ", e)
                pass
            else:
                raise
        finally:  

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