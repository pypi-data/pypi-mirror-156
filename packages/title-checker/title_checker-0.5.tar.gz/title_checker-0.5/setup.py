import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='title_checker',  
     version='0.5',
    scripts=['title_checker'] ,
     author="Mojtaba Monfared",
     author_email="4lientears@gmail.com",
     description="A Python script for checking the titles of each youtube links in a text file",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/MojtabaMonfared/title_checker",
     packages=setuptools.find_packages(),
     install_requires=[
            'selenium',
            'typer',
            'questionary'
        ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
     ],
 )