from setuptools import setup, find_packages



# Setting up
setup(
    name="academylibrary",
    version='0.0.1',
    author="Gilad Korngut",
    author_email="theacademy4summer@gmail.com",
    description="Academy4Summer Package",
    long_description_content_type="text/markdown",
    long_description='For The Academy4summer Course',
    packages=find_packages(),
    install_requires=['discord','pyautogui'],
    keywords=['python', 'Course','Discord'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
