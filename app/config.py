import os
import warnings
from dotenv import load_dotenv
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))
app_basedir = Path(__file__).parents[1]

env_file = Path(app_basedir, ".env")
if env_file.exists():
    load_dotenv(env_file)
else:
    warnings.warn("No .env file found.")

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'RedBand-dfdfd-dfd'

    APP_ID = "kurm_de_playground"
    ACCESS_KEY = "ttn-account-v2.3nxT_GinCYFrgO0naCoZH38LYqNYYiqtqct71Uam3Og"

    APP_ID1 = "ttn_bernd_mapper"
    ACCESS_KEY1 = "ttn-account-v2.aW7zKW0fKZaOl4g5Y_M3evxSRZJs5EdymCMTuYMnmzM"

    password = os.environ.get("MYSQL_PASSWORD")
    username = os.environ.get("MYSQL_USER")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + username + ':' + password + '@localhost/ffrs_ttn_map'
    SQLALCHEMY_TRACK_MODIFICATIONS = False