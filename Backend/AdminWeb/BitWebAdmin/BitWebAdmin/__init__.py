"""
The flask application package.
"""
import logging
from flask import Flask
from applicationinsights.flask.ext import AppInsights

app = Flask(__name__)
app.config.from_object('config_cosmos')
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = 'e91ec904-dc0b-4a2f-b9a5-22114024e3b1'
# log requests, traces and exceptions to the Application Insights service
appinsights = AppInsights(app)

import BitWebAdmin.views