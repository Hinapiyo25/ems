"""WSGI entry point for production hosting.

Used by gunicorn on Render / Railway / Fly.io and by PythonAnywhere:

    gunicorn wsgi:application

Local development still uses `python app.py` (which runs the Flask dev server
with auto-reload).
"""

from app import create_app

application = create_app()
app = application
