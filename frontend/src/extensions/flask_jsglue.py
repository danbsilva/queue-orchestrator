from flask_jsglue import JSGlue

jsglue = JSGlue()


def init_app(app):
    jsglue.init_app(app)