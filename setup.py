# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path



here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = fh.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='pps_gui',  # Required
    version='2.024',  # Required
    description='A software based Raspberry Pi type simulator to aid in teaching Python, requires pps_emu.',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/chuckwhealton/pps_gui',  # Optional
    author='Charles R. Whealton',  # Optional
    author_email='chuck@dtcc.edu',  # Optional
    classifiers=[  # Optional
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],

    keywords='ITN 160',  # Optional

    packages=find_packages(),  # Required

    install_requires=['guizero', 'pygame'],  # Optional

    package_data={  # Optional
        'pps_gui': ['buzzer.wav', 'Day.png',
                    'Night.png', 'Ouch.png'],
    },

  


entry_points={  # Optional
        'console_scripts': [
            'pps_gui=pps_gui:main',
        ],
    },	# Optional

)