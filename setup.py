from setuptools import setup

setup(
    name='log21',
    version='2',
    py_modules=['log21'],
        install_requires=[
            'Click',
    ],
    entry_points='''
        [console_scripts]
        log21=log21:cli
        log21-sensor=log21:cli_sensor
    ''',
)
