from importlib import import_module

def load(app):
    for extension in app.config['EXTENSIONS']:
        module_name, factory = extension.split(":")
        ext = import_module(module_name)
        getattr(ext, factory)(app)