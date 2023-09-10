import os
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('shared.env')


from src import app

main_app = app.create_app()


if __name__ == '__main__':


    host = os.getenv("APP_HOST")
    port = os.getenv("APP_PORT")
    debug = os.getenv("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)