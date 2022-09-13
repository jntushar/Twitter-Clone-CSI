from modules import app
from config import *

if __name__ == '__main__':
    app.run(host=listen_host, port=listen_port, debug=True)
