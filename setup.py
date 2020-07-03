from distutils.core import setup
from code_bert import __version__


setup(
name='CodeBERT',
version=__version__,
packages=['code_bert',],
entry_points = {
    'console_scripts': ['create_training_data=code_bert.cli.training_data_prep:main',
                        'generate_train_command=code_bert.cli.generate_train_script:main',
                        'download_model=code_bert.cli.download_model:main',
                        'run_pipeline=code_bert.cli.run_pipeline:main'],
},
license='Creative Commons Attribution-Noncommercial-Share Alike license',
)