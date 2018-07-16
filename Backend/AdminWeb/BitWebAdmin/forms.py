from flask_wtf import Form
from wtforms import StringField

class GameAdminForm(Form):
	game_locale = StringField()