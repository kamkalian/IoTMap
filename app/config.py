import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'RedBand-dfdfd-dfd'

    password = os.environ.get("MYSQL_PASSWORD")
    username = os.environ.get("MYSQL_USER")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + username + ':' + password + '@localhost/ffrs_ttn_map'
    SQLALCHEMY_TRACK_MODIFICATIONS = False