from setuptools import setup, find_packages

setup(
    name="simulate-dynamic-energy",
    version="0.1.0",
    description="Dynamic Energy Analysis Application",
    author="ANierbeck",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "requests",
        "python-dotenv",
        "influxdb-client",
        "influxdb",
        "homeassistant-api",
        "streamlit",
        "plotly",
        "altair",
        "pytest",
        "pytest-cov",
        "python-dateutil",
    ],
    python_requires=">=3.11",
)