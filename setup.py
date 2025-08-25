from setuptools import setup, find_packages

setup(
    name="agrosoft",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Django==5.2",
        "django-cors-headers==4.3.1", 
        "django-debug-toolbar==4.3.0",
        "django-extensions==3.2.3",
        "gunicorn==22.0.0",
        "whitenoise==6.7.0",
        "dj-database-url==2.1.0",
        "psycopg2-binary==2.9.9",
        "Pillow==9.5.0",
        "python-decouple==3.8",
        "requests==2.31.0",
        "Werkzeug==3.0.1",
    ],
)
