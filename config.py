import os
dirname = os.path.dirname(__file__)
txtpath = os.path.join(dirname, 'megilot/static/texts/uploads')

class Config(object):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = False
    TEXT_UPLOADS = txtpath
    ALLOWED_FILE_EXTENTIONS = ["TXT"]
    MAX_CONTENT_LENGTH = 8 *1024 * 1024
    SECRET_KEY = 'or5HPckRdk-ztsfOUak4fA'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False