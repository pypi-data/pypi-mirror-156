from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='LRF utils',
    url='https://github.com/LeiRoF/Utils',
    author='Vincent Foriel',
    author_email='vince.lrf@gmail.com',
    install_requires=['numpy'],
    version='0.2',
    description="Just a custom library to share with some colleagues.",
    long_description=open('README.md').read(),
)