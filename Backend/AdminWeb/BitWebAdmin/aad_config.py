TENANT = "aubitdemo.onmicrosoft.com"  # Enter tenant name, e.g. contoso.onmicrosoft.com
AUTHORITY_HOST_URL = "https://login.microsoftonline.com"
AUTHORITY_URL = AUTHORITY_HOST_URL + '/' + TENANT
CLIENT_ID = "921096fc-8ae8-4962-9dcf-719ba14101c9"  # copy the Application ID of your app from your Azure portal
CLIENT_SECRET = "Ehkp44l54bfDP666mWiQTRLLelel9+F7Q3KP1YTSIgE="
RESOURCE = "https://graph.windows.net"
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')