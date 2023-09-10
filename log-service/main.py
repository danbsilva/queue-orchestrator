import os
from dotenv import load_dotenv


# Load shared  and project variables
load_dotenv('.env')
load_dotenv('shared.env')


from src import app, register, threads

# Return Flask app
main_app = app.create_app()

# Register service in API Gateway
register.service(app=main_app)

# Execute threads
threads.execute(app=main_app)

if __name__ == '__main__':

    host = os.getenv("APP_HOST")
    port = os.getenv("APP_PORT")
    debug = os.getenv("DEBUG")
    #main_app.run(host=host, port=port, debug=debug, use_reloader=debug)
