from setuptools import setup
from setuptools import find_packages

VERSION = '0.0.1'

setup(
	name='autohome_push',  # package name
	version=VERSION,  # package version
	description="""a tools that processing feature
	ensure feature consistency when training and reasoning
	""",
	author='hisoka',
	maintainer_email='libin16104@autohome.com.cn',
	keywords='pyspark;machine learning',
	url='https://github.com/hisoka176/push',
	python_requires='==2.7',
	packages=find_packages(),
	zip_safe=False,
	install_requires=['pyspark==2.4.6']

)
