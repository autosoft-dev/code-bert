from distutils.core import setup
from code_bert import __version__


setup(
name='CodeBERT',
version=__version__,
packages=['code_bert',],
# entry_points = {
#     'console_scripts': ['codistai_data_fetcher=codistai_assist.apps.process_repos:main'],
# },
license='Creative Commons Attribution-Noncommercial-Share Alike license',
)