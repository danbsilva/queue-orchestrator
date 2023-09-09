def load(app):

    @app.route('/health/', methods=['GET'])
    def health():
        return 'OK'
