import os
from flask import Flask
from routes.main_routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

    # registra as rotas
    app.register_blueprint(main_bp)

    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=True)
