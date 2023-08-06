import setuptools

setuptools.setup(

    name='iothello',
    version='1.1.1',

    author='Thomas Compagnoni',
    author_email='thomascompagnoni@gmail.com',
    description='Welcome to iOthello_package, a project which leverages the power of machine learning to create an AI-Bot for Othello.',
    url='https://github.com/ThomasMind/iOthello',
    license='MIT LICENCE',

    install_requires=['numpy', 'pygame', 'joblib'],

    packages=setuptools.find_packages(),
    package_data={'': ['font.otf', 'models/*.sav']},
    include_package_data=True,

)
