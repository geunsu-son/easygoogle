from setuptools import setup, find_packages
import os

# Read version from __version__.py
version = {}
with open(os.path.join("gs_utils", "__version__.py")) as f:
    exec(f.read(), version)

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name='gs_utils',
    version=version['__version__'],
    description='Simple and powerful Python wrapper for Google APIs (Drive, Sheets)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='geunsu-son',
    author_email='gnsu0705@gmail.com',
    url='https://github.com/geunsu-son/gs_utils',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*', 'docs', 'docs.*']),
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business',
    ],
    keywords='google api drive sheets gspread pydrive wrapper google-api-python-client',
    project_urls={
        'Bug Reports': 'https://github.com/geunsu-son/gs_utils/issues',
        'Source': 'https://github.com/geunsu-son/gs_utils',
        'Documentation': 'https://github.com/geunsu-son/gs_utils#readme',
    },
    include_package_data=True,
)
