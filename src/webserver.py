import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot activo.'

def keep_alive():
    port = int(os.environ.get('PORT', 5000))
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    t.daemon = True
    t.start()
    print(f'Servidor web activo en http://localhost:{port}')
