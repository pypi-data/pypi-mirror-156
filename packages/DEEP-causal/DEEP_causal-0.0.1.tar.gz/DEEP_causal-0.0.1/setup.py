from setuptools import setup

setup(
    name='DEEP_causal',
    version='0.0.1',
    author='Shisheng Zhang',
    author_email='shisheng.zhang@mymail.unisa.edu.au',
    url='https://github.com/JuliusZSS/DEEP_causal',
    description=u'DEEP_causal',
    packages=['DEEP_causal'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'test1=DEEP_causal:test1',
            'test2=DEEP_causal:test2'
        ]
    }
)