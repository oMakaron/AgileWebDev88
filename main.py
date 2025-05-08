from app import create_app
from config import DeploymentConfig


flask_app = create_app(DeploymentConfig)

if __name__ == '__main__':
    flask_app.run()
