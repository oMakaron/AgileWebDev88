from flask import Flask

# Tell Flask where to find the static folder
app = Flask(
    __name__,
    static_folder='../static',         # static is outside /app
    template_folder='templates'        # templates are inside /app
)

# TODO: Make this not absolutely suck
app.secret_key = 'very-secret'

from app import routes

if __name__ == '__main__':
    app.run(debug=True)
