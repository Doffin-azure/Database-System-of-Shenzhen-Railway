class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://mysql:mysql@localhost:3306/project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
