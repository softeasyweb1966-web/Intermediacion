import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    use_reloader = os.getenv("FLASK_USE_RELOADER", "0") == "1"
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=use_reloader)
