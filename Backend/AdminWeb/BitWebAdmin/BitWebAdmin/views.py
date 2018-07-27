"""
Routes and views for the flask application.
"""

import operator
from PIL import Image, ImageDraw, ImageOps
import requests
import io
from io import BytesIO
import random
import cognitive_face as CF
import face_config
import storage_config
from forms import GameAdminForm, ConfirmUserForm, FindUserForm, EventAdminForm
from flask_wtf import Form
from wtforms.fields import StringField, BooleanField
from wtforms.validators import InputRequired
import config_cosmos
import pydocumentdb
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
from azure.storage.blob import BlockBlobService, ContentSettings
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

@app.route('/eventadmin', methods=['GET', 'POST'])
def eventadmin(): 
    form = EventAdminForm()

    # Create a model to pass to results.html
    class EventAdminObject:
        game_locale = ""
        person_group_id = ""

    admin_form_object = EventAdminObject()

    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

    doc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.GAME_CONFIG_COSMOSDB_COLLECTION + '/docs/' + config_cosmos.GAME_CONFIG_COSMOSDB_DOCUMENT)


    if form.validate_on_submit():

        doc['activeevent'] = form.event_location
        doc['persongroupid'] = form.person_group
        # replaced_document = client.ReplaceDocument(doc['_self'], doc)


    else:


        admin_form_object.game_locale = doc['activeevent']
        admin_form_object.person_group_id = doc['persongroupid']

    return render_template(
        'eventadmin.html', 
        year=datetime.now().year,
	    admin_form_object = admin_form_object,
	    form = form)

@app.route('/gameadmin', methods=['GET', 'POST'])
def gameadmin(): 
    form = GameAdminForm()

    # Create a model to pass to results.html
    class GameAdminObject:
        game_round = 0

    admin_form_object = GameAdminObject()

    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})

    doc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.GAME_CONFIG_COSMOSDB_COLLECTION + '/docs/' + config_cosmos.GAME_CONFIG_COSMOSDB_DOCUMENT)

    if form.validate_on_submit():
         
        doc['activetier'] = int(form.game_round.data)
        replaced_document = client.ReplaceDocument(doc['_self'], doc)

        try:

            # Select confirmed users that haven't been Bit before. Support groups of up to 1,000 players because that's the max for a standard Person Group in Face API.
            query = {
                    "query": "SELECT TOP 1000 u.id FROM u WHERE u.confirmed=true AND u.byteround=0",
                    }
     
            results = list(client.QueryDocuments('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION, query))

            # total available users 
            item_count = len(results)
            # select a random integer representing position in list to select
            user_to_select = random.randint(0,item_count-1)
            # select new Bit user from list - list consists of document ID
            new_bit_user = results[user_to_select]

            # Read the full Cosmos document for the user
            userDoc = client.ReadDocument('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_COSMOSDB_COLLECTION + '/docs/' + new_bit_user['id'])

            
       
            # Load Image for selected play (we know they have one because we eyeball it before confirming them at the stand)

            options = {} 
            options['maxItemCount'] = 1

            # Select image for user (may be multiple so we will take only 1). Ensure it's an image with a valid Face ID and rectangle and not just a random image
            query = {
                    "query": "SELECT * FROM u WHERE u.userid=@userId AND u.faceid<>'' and u.faceRectangle != null",
                    "parameters" : [
                            { "name": "@userId", "value": new_bit_user['id'] }
                        ]
                    }

            # Load the static Bit character image (has alpha background)
            bitImgResponse = requests.get("https://whereisbitdev01.blob.core.windows.net/bitsource/ScottGu.png?sp=r&st=2018-07-25T22:43:24Z&se=2019-07-26T06:43:24Z&spr=https&sv=2017-11-09&sig=KgJP4ShxZ%2BE4cJd%2B5MPSu5CJn9kix226mIK2%2BtXymDE%3D&sr=b")
            bitImage = Image.open(BytesIO(bitImgResponse.content))      

            # Load one of the player's selfies
            images = list(client.QueryDocuments('dbs/' + config_cosmos.COSMOSDB_DATABASE + '/colls/' + config_cosmos.USERS_IMAGES_COSMOSDB_COLLECTION, query, options))
            playerImageUrl = images[0]['imgurl']
            faceId = images[0]['faceid']
            rectTop = images[0]['faceRectangle']['top']
            rectLeft = images[0]['faceRectangle']['left']
            rectRight = rectLeft + images[0]['faceRectangle']['width']
            rectBottom = rectTop + images[0]['faceRectangle']['height']

            playerImgResponse = requests.get(playerImageUrl)
            playerImage = Image.open(BytesIO(playerImgResponse.content))

            # Resize static Bit image to be smaller that selfie
            resizedBitImage= ImageOps.fit(bitImage, (images[0]['faceRectangle']['width'], images[0]['faceRectangle']['height']))
        
            # Uncomment to draw a rectangle where the face rectangle has been determined.
            #dr = ImageDraw.Draw(playerImage)
            #dr.rectangle((rectLeft, rectTop, rectRight, rectBottom), outline="red")

            # Paste Bit into the player's selfie, using alpha mask from Bit image.
            playerImage.paste(resizedBitImage,(rectLeft, rectTop, rectRight, rectBottom),resizedBitImage)

            # Upload merged image to Blob storage so we can serve on big screen.        
            imgByteArr = io.BytesIO()
            playerImage.save(imgByteArr,'PNG')
            block_blob_service = BlockBlobService(account_name=storage_config.STORAGE_ACCOUNT, account_key=storage_config.STORAGE_KEY)
            block_blob_service.create_blob_from_bytes(storage_config.BIT_IMAGE_CONTAINER, faceId +".png", imgByteArr.getvalue(), content_settings=ContentSettings(content_type='image/png'));
        
            bitly_user_handle = new_bit_user['id']
            bitly_blob_url = 'https://' + storage_config.STORAGE_ACCOUNT + '.blob.core.windows.net/' + storage_config.BIT_IMAGE_CONTAINER + '/' + faceId + '.png'

            #####
            # If images processed OK then write content to Cosmos

            # Set the round ID to be the currently selected round.
            userDoc['byteround'] = int(form.game_round.data)
            # Write document back to Cosmos
            client.ReplaceDocument(userDoc['_self'], userDoc)


        except errors.DocumentDBError as e:

            tc.track_exception(e)
            tc.flush()

            if e.status_code == 404:
                print("Document doesn't exist")
            elif e.status_code == 400:
                # Can occur when we are trying to query on excluded paths
                print("Bad Request exception occured: ", e)
                pass
            else:
                raise

        except Exception as ex:
            tc.track_exception(ex)
            tc.flush()


        finally:  

            return render_template(
                'saved.html',
                bitly=bitly_user_handle,
                bitlyurl=bitly_blob_url,
                year=datetime.now().year)

        #return render_template(
        #    'gameadmin.html', 
        #    year=datetime.now().year,
	       # form = form)

        
    else:
    
        # load existing values into the form

        form.game_round.data = doc['activetier']

        admin_form_object.game_round = doc['activetier']
                
        return render_template(
            'gameadmin.html', 
            year=datetime.now().year,
		    admin_form_object = admin_form_object,
		    form = form)