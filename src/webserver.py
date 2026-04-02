from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot activo.'

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    t.daemon = True
    t.start()
    print('Servidor web activo en http://localhost:5000')
