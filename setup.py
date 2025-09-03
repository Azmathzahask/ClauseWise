from setuptools import setup, find_packages

setup(
    name='clausewise',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='AI-powered legal document analyzer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/clausewise',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'transformers',
        'torch',
        'pandas',
        'numpy',
        'scikit-learn',
        'nltk',
        'spacy',
        'flask'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)