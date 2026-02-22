from setuptools import setup, find_packages

setup(
    name="gradcafe_analyzer",
    version="1.0.0",
    description="JHU Software Concepts: GradCafe Admissions Analyzer",
    author="Masaomi Enami",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "psycopg",
        "python-dotenv",
        "beautifulsoup4"
    ],
)