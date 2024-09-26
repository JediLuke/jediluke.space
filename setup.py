from setuptools import setup

def read_requirements():
	with open('requirements.txt') as req:
		content = req.read()
		requirements = content.split('\n')

	return requirements	

setup(
	name='live_site',
	version='1.0',
	py_modules=['live_site'],
	install_requires=read_requirements(),
	entry_points='''
		[console_script]
		live_site=live_site:main
	'''
)