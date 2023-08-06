from setuptools import setup, find_packages

setup(
    name='akxvau',
    packages=find_packages(),
    include_package_data=True,
    version="0.0.1",
    description='AKXVAU LINKTREE',
    author='AKXVAU',
    author_email='akxvau@gmail.com',
    long_description=(open("README.md","r")).read(),
    long_description_content_type="text/markdown",
   install_requires=['lolcat'],
 
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
                'akxvau = akxvau.akxvau:menu',
                
            ],
    },
    python_requires='>=3.9'
)
