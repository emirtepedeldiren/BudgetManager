from setuptools import setup

APP = ['budget_manager.py'] 
DATA_FILES = []
OPTIONS = {
    'iconfile': 'icon.icns', 
    'packages': ['customtkinter', 'requests'], 
    'plist': {
        'LSUIElement': False, 
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)