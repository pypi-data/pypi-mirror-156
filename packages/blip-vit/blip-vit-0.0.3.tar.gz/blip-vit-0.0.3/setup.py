from distutils.core import setup
from pip._internal.req import parse_requirements

requirements = [
    ir.requirement for ir in parse_requirements(
        'requirements.txt',
        session='test')]

setup(
    name='blip-vit',
    packages=['blip', 'blip.models', 'blip.configs'],
    version='0.0.3',  # Ideally should be same as your GitHub release tag varsion
    description='BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation',
    author='salesforce',
    author_email='junnan.li@salesforce.com',
    url='https://github.com/fernandoTB/BLIP',
    download_url='https://github.com/fernandoTB/BLIP/archive/refs/tags/0.0.3.tar.gz',
    keywords=['0.0.3'],
    install_requires=requirements,
    classifiers=[],
    package_data={'': [
        '*.txt',
        '*.yaml',
        '*.json'
    ]}
)
