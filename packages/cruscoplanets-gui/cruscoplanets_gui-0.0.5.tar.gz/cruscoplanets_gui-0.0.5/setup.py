import os
import setuptools

if __name__ == '__main__':
	with open("README.md", 'r') as long_file:
		long_descript = long_file.read()
	setuptools.setup(
		name='cruscoplanets_gui',
		version='0.0.5',
		packages=setuptools.find_packages(),
		entry_points={
			'gui_scripts': [
				'cruscoplanets_gui = cruscoplanets_gui.__main__:main',
			],
			'console_scripts': [
				'cruscoplanets_gui = cruscoplanets_gui.__main__:main',
			],
		},
		install_requires=[
			'wheel',
			'cruscoplanets>=0.3.1',
			'langcodes[data]',
			'pycountry==22.3.5',
			'PyQt5==5.15.4'
		],
		python_requires='==3.8.10',
		package_data={'cruscoplanets_gui': ['config/base.txt']},
		author='Emiliano Minerba',
		author_email='emi.nerba@gmail.com',
		description="GUI interface for the cruscoplanets package",
		long_description=long_descript,
		long_description_content_type='text/markdown',
		license='GPL',
		url='https://gitlab.com/kikulacho92/cruscoplanets_gui',
		keywords='astrology Morpurgo dialectic charts'
	)
