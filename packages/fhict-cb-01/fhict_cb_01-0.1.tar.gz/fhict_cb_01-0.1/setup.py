from setuptools import setup, find_packages


setup(
    name='fhict_cb_01',
    version='0.1',
    license='MIT',
    author="Author Name",
    author_email='email@example.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/adamatei/pypi-package',
    keywords='test project',
    python_requires=">=3.7.0",
    install_requires=[
        'flask-login',
        'sqlalchemy',
        #'setuptools',
        #'six==1.16.0',
        # 'sqlite==3.36',
        'flask>=2.0.2',
        #'colorama==0.4.4',
        'pymata4>=1.15'
    ],

)
