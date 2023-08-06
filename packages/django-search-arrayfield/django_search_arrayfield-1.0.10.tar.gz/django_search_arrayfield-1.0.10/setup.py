from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.10'
DESCRIPTION = 'Dynamic Search in Array Field in Django Admin'
LONG_DESCRIPTION = 'A package that allows Dynamic Search in Array Field in Django Admin'

# Setting up
setup(
    name="django_search_arrayfield",
    version=VERSION,
    author="Arshan Ahmad , Shivaank Tripathi",
    author_email="<arshan@thetarzanway.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages = ['.','django_search_arrayfield.templates','django_search_arrayfield.static'],

    package_data={'django_search_arrayfield.templates':['*'],'django_search_arrayfield.static':['*']},  
#     packages=find_packages(),
#     package_data = {
#     'static': ['*'],
#     'template': ['*']
# },
    install_requires=[],
    keywords=['python', 'django_better_admin', 'dynamic_search', 'dynamic-search', 'django-admin'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)