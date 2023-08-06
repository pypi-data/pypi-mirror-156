import os
from setuptools import setup, find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name='sutra',
    version='0.2.2',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A python package for calculating the removal of microbial organisms in the subsurface',
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Hydrology',
    ],
    python_requires='>=3.7',
    project_urls={
    'Source': 'https://github.com/KWR-Water/sutra',
    'Documentation': 'http://sutra.readthedocs.io/en/latest/',
    'Tracker': 'https://github.com/KWR-Water/sutra/issues',
    'Help': 'https://github.com/KWR-Water/sutra/issues',
    # 'Help': 'https://stackoverflow.com/questions/tagged/sutra'
    },
    install_requires=[
        'pandas>=0.23',

        ],
    include_package_data=True,
    url='https://github.com/KWR-Water/sutra',
    author='KWR Water Research Institute',
    author_email='martin.korevaar@kwrwater.nl, martin.van.der.schans@kwrwater.nl, steven.ros@kwrwater.nl, alex.hockin@kwrwater.nl',
)
