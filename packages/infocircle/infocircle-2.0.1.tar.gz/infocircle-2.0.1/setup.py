from setuptools import setup, find_packages

setup(
    name='infocircle',
    packages=find_packages(),
    include_package_data=True,
    version="2.0.1",
    description='ROBI CIRCLE INFORMATION FINDER',
    author='AKXVAU',
    author_email='admin@itzakx.com',
    long_description=(open("README.md","r")).read(),
    long_description_content_type="text/markdown",
   install_requires=['lolcat', 'requests'],
 
    keywords=['AKXVAU'],
    classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
            'Environment :: Console',
    ],
    
    license='MIT',
    entry_points={
            'console_scripts': [
                'infocircle = infocircle.infocircle:menu',
                
            ],
    },
    python_requires='>=3.9'
)
