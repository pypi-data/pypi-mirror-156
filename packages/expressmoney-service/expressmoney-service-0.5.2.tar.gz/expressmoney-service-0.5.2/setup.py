"""
py setup.py sdist
twine upload dist/expressmoney-service-0.5.2.tar.gz
"""
import setuptools

setuptools.setup(
    name='expressmoney-service',
    packages=setuptools.find_packages(),
    version='0.5.2',
    description='Remote services',
    author='Development team',
    author_email='dev@expressmoney.com',
    install_requires=('expressmoney',),
    python_requires='>=3.7',
)
