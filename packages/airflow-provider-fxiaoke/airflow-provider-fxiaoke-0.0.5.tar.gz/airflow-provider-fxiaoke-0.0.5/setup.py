from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

"""Perform the package airflow-provider-fxiaoke setup."""
setup(
    name='airflow-provider-fxiaoke',
    version="0.0.5",
    description='Airflow plugins for fxiaoke CRM(ShareCRM) api.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        "apache_airflow_provider": [
            "provider_info=airflow_fxiaoke.__init__:get_provider_info"
        ]
    },
    license='Apache License 2.0',
    packages=['airflow_fxiaoke', 'airflow_fxiaoke.hooks',
              'airflow_fxiaoke.operators'],
    install_requires=[
        'apache-airflow>=2.1',
        'fxiaoke-python>=0.0.1',
        'apache-airflow-providers-google>=6.0.0'
    ],
    setup_requires=['setuptools', 'wheel'],
    author='wbin',
    author_email='wbin.chn@gmail.com',
    url='https://github.com/wbchn/apache-airflow-providers-fxiaoke',
    python_requires='~=3.8',
)
