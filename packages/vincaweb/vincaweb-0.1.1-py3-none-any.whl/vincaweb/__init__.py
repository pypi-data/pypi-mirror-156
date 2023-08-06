from flask import Flask
vincaweb = Flask(__name__)
from vincaweb import routes
vincaweb.run(debug=True)
