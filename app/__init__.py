from flask import Flask

app = Flask(__name__)

# TODO: Make this not absolutely suck
app.secret_key = 'very-secret'

from app import routes

if __name__ == '__main__':
    app.run()

