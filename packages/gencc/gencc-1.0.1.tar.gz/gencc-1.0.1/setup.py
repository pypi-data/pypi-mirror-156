from setuptools import setup, find_packages

setup(
    name='gencc',
    packages=find_packages(),
    include_package_data=True,
    version="1.0.1",
    description='CC GENERATOR FOR BIN',
    author='AKXVAU',
    author_email='admin@itzakx.ml',
    long_description=(open("README.md","r")).read(),
    long_description_content_type="text/markdown",
   install_requires=['lolcat'],
 
    keywords=['GENCC', 'BIN', 'CC GENERATOR', 'CRADIT CARD NUMBER', 'AKXVAU', 'DCBD04', 'DEVS COMMUNITY', 'DEV COMMUNITY', 'MOHAMMAD ALAMIN'],
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
                'gencc = gencc.gencc:akx_main',
                
            ],
    },
    python_requires='>=3.9'
)
