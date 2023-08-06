from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Integration SAML2.0 OKTA'

setup(
    name="MSArqAuth",
    version=VERSION,
    author="Radkasens",
    author_email="marredondoe@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['datetime','uuid','PyJWT','requests'],
    keywords=['SAML2.0','OKTA'],
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)