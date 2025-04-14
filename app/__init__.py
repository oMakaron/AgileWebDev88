from flask import Flask

app = Flask(__name__)
app.secret_key = 'very-secret'

from app import routes

if __name__ == '__main__':
    app.run()

