from flask_dotenv import DotEnv
class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:superstar9@localhost/asset_code_names'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY='1f1fdd7984b8653db6eee150af30c029'
    @classmethod
    def init_app(self, app):
        env = DotEnv()
        env.init_app(app)