from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = 'Programmes propositional logic reasonings among the concepts learned by other neural networks'


setup(
       
        name="pienex", 
        version=VERSION,
        author="Alejandro Ascárate",
        author_email="<aleazk@gmail.com>",
        description=DESCRIPTION,
        readme = "README.md",
        packages=find_packages(),
        install_requires=["NumPy", "Keras", "TensorFlow"], 
        
        keywords=['python', 'propositional logic'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)