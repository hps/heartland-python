from distutils.core import setup

setup(
    name='SecureSubmit',
    version='2.5.4',
    author='Heartland Payment Systems',
    author_email='EntApp_DevPortal@e-hps.com',
    packages=[
        'securesubmit',
        'securesubmit.applepay',
        'securesubmit.entities',
        'securesubmit.infrastructure',
        'securesubmit.services',
        'securesubmit.services.fluent',
        'securesubmit.tests',
        'securesubmit.tests.applepay',
        'securesubmit.tests.fluent',
        'securesubmit.tests.payplan',
        'securesubmit.tests.certification'
    ],
    scripts=[],
    url='http://developer.heartlandpaymentsystems.com/SecureSubmit',
    license='LICENSE.txt',
    description='SDK for integrating with the Heartland Portico Gateway',
    long_description=open('README.txt').read(),
    install_requires=[
        'xmltodict >= 0.9.0',
        'jsonpickle >= 0.6.1',
        'enum >= 0.4.4',
        'requests >= 2.1.0']
)
