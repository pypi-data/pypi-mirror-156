from setuptools import setup

requirements = ['pandas>=0.25.1', 'numpy>=1.17.2']

setup(
    name='prediction_coefficient',
    version='0.0.0',
    description="A categorical correlation coefficient that's in the same range for all pairs of variables (from 0 to 1), regardless of their degrees of freedom or the chosen confidence level. Provides a correlation matrix.",
    license="Copyright ©2022 by Lance Edward Darragh. All rights reserved. This software may be used for free. This software may not be reproduced or distributed without the author's written consent. To obtain consent, contact the author at ForDataScience@gmx.com. Prediction Coefficient™",
    author="Lance Darragh",
    author_email='ForDataScience@gmx.com',
    url='https://github.com/ForDataScience/prediction_coefficient',
    packages=['prediction_coefficient'],
    
    install_requires=requirements,
    keywords='prediction_coefficient',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
