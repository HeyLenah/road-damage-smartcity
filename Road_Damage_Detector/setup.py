from setuptools import setup, find_packages

setup(
    name='road_damage_detector',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'ultralytics',
        'matplotlib',
        'pandas',
        'opencv-python-headless',
        'seaborn',
        'Pillow',
        'roboflow'
    ],
    description='Model for detecting road damage',
    python_requires='>=3.10.6',
)
