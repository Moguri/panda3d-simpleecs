from setuptools import setup


__version__ = ''
#pylint: disable=exec-used
exec(open('simpleecs/version.py').read())


setup(
    name='panda3d-simpleecs',
    version=0.1,
    keywords='panda3d gamedev ecs',
    packages=['simpleecs'],
    install_requires=[
        'panda3d',
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'panda3d',
        'pytest',
        'pylint==2.3.*',
        'pytest-pylint',
    ],
)
