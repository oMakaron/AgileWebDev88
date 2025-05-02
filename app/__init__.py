from flask import Flask

# Tell Flask where to find the static folder
app = Flask(
    __name__,
    static_folder='../static',
    template_folder='templates'
)

# TODO: Make this not absolutely suck
app.secret_key = 'very-secret'

from app import routes

if __name__ == '__main__':
    app.run(debug=True)
