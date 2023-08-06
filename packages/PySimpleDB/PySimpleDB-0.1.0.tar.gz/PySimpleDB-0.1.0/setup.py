import setuptools
with open(r'C:\Users\Ростислав\Downloads\readme.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='PySimpleDB',
	version='0.1.0',
	author='Super_Zombi',
	author_email='super.zombi.yt@gmail.com',
	description='Simple json database',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/SuperZombi/Py-Simple-DB',
	packages=['PySimpleDB'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)