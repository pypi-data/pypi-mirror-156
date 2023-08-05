from setuptools import setup, find_packages

with open('requirements.txt') as f:
	requirements = f.readlines()

long_description = 'Sample Package made for a demo'

setup(
		name ='nidhi',
		version ='1.0.0',
		author ='nidhi patel',
		author_email ='nidhijp31@gmail.com',
		url ='https://github.com/Vibhu-Agarwal/vibhu4gfg',
		description ='Demo Package for GfG Article.',
		long_description = long_description,
		long_description_content_type ="text/markdown",
		license ='MIT',
		packages = find_packages(),
		entry_points ={
			'console_scripts': [
				'nidhi = test.tfmanger:main'
			]
		},
		classifiers =(
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
		),
		keywords =' article python package ',
		install_requires = requirements,
		zip_safe = False
)
