from decouple import config as config_env
from src import app, register


main_app = app.create_app()

# Thread to consumer topic SERVICES REGISTER
register.register_service(main_app)

if __name__ == '__main__':

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)
