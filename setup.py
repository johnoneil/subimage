from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='subimage',
    version='0.1',
    description='Find images within other images.',
    long_description = readme(),
	classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Image Recognition',
      ],
    keywords = 'Image recognition find subimage processing',
    url='https://github.com/johnoneil/subimage',
    author='John O\'Neil',
    author_email='oneil.john@gmail.com',
    license='MIT',
    packages=['subimage'],
    install_requires=[
        'numpy',
        'scipy',
        'argparse'
      ],
    entry_points = {
		'console_scripts': [
			'subimage-find-aspect-ratio=subimage.find_by_ar:main',
			'subimage-find=subimage.find_subimage:main',			
			],
    },
      zip_safe=True)
