from setuptools import setup, find_packages

setup(
    name="astratrade",
    version="0.1.0",
    packages=find_packages(include=["apps", "apps.*"]),
    install_requires=[
        # Add dependencies here if needed (e.g., "fastapi", "pytest")
    ],
)