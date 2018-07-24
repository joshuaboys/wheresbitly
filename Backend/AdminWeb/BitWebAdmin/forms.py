from flask_wtf import Form
from wtforms.validators import InputRequired
from wtforms import StringField, BooleanField, HiddenField

class GameAdminForm(Form):
    event_location = StringField('Event Location')
    person_group = StringField('Person Group')
    game_round = StringField('Game Round')

class FindUserForm(Form):
    user_name = StringField('Twitter Handle',[InputRequired()])

class ConfirmUserForm(Form):
    user_name = HiddenField()
    user_confirmed = BooleanField('Confirm Player')
