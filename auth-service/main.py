import os
from dotenv import load_dotenv

# Load shared  and project variables
load_dotenv('shared.env')
load_dotenv('.env')


from src import app, register


# Create app
main_app = app.create_app()

# Thread to consumer topic SERVICES REGISTER
register.service(main_app)

if __name__ == '__main__':

    host = os.getenv("APP_HOST")
    port = os.getenv("APP_PORT")
    debug = os.getenv("APP_DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)
