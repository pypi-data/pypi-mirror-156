from setuptools import find_packages, setup

setup(
    name='avocados',
    version='1.0.4',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['manage.py'],
    install_requires=[
        'django',
        'djangorestframework',
        'pygments',
        'pytest',
        'avocadopml'
    ],
)