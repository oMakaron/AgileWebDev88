from app import create_app
from config import DeploymentConfig
from dotenv import load_dotenv


load_dotenv()
flask_app = create_app(DeploymentConfig)

if __name__ == '__main__':
    flask_app.run(debug=True)
