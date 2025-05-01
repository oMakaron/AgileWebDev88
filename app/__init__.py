from flask import Flask
from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import CSRFProtect

# Tell Flask where to find the static folder
app = Flask(
    __name__,
    static_folder='../static',
    template_folder='templates'
)

app.secret_key = 'very-secret'

csrf = CSRFProtect(app)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

from app import routes
