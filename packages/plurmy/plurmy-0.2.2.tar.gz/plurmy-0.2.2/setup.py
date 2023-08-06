from setuptools import setup, find_packages

setup(
    name="plurmy",
    version="0.2.2",
    license='CC0-1.0',
    long_description="",
    packages=find_packages(),
    include_package_data=True,
    install_requires = [
     'hiredis',
     'python>=3.7',
     'redis',
     'redis-py' 
    ],
    entry_points = {
        'console_scripts': [
            'plurmy = plurmy.orchestrate:main',
        ]
    }
)
