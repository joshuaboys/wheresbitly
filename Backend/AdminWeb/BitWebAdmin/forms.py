from flask_wtf import Form
from wtforms import StringField

class GameAdminForm(Form):
    event_location = StringField('Event Location')
    person_group = StringField('Person Group')
    game_round = StringField('Game Round')
