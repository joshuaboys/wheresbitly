from flask_wtf import Form
from wtforms.validators import InputRequired
from wtforms.fields import StringField, BooleanField, HiddenField, SelectField

class EventAdminForm(Form):
    event_location = StringField('Event Name', [InputRequired()])
    person_group = StringField('Person Group', [InputRequired()])

class GameAdminForm(Form):
    game_round = SelectField('Game Round', coerce = int)

class FindUserForm(Form):
    user_name = StringField('Twitter Handle', [InputRequired()])

class ConfirmUserForm(Form):
    user_name = HiddenField()
    user_confirmed = BooleanField('Confirm Player', [InputRequired()])