import os
from glob import glob
from distutils.core import setup

setup_kwargs = dict()

template_files = [('templates',[]),('templates/deprovision.tpl.example',[])]
conf_files = [('conf',glob('conf/worker.cfg.example'))]

setup(
    name='squarepulse',
    version='0.1',
    packages = ['squarepulse'],
    url='http://github.com/LarsFronius/squarepulse',
    license='',
    author='LarsFronius',
    author_email='l.fronius@googlemail.com',
    description='',
    install_requires=['django'],
    package_dir={'' : 'lib'},
    scripts=glob('bin/*'),
    data_files=template_files + conf_files,
    **setup_kwargs
)
