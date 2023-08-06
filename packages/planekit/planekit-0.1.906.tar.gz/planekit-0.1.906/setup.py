from distutils.core import setup
import setuptools


VERSION = "0.1.906"  # BURAYI AKLINIZDA TUTUN (Değiştirebilirsiniz)
long_description = ""
with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()
setup(
    name='planekit',
    packages=setuptools.find_packages(),
    install_requires=['pymavlink==2.4.29', 'pyserial==3.5'],
    options={"bdist_wheel": {"universal": True}},
    version='0.1.906',
    license='MIT',
    description='Developer Tools for Fixed-wing',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Musa Şen',
    author_email='m42@gmail.com',
    url='https://github.com/msasen/planekit',

    download_url=f'https://github.com/msasen/planekit{VERSION}.tar.gz',
    keywords=['Planekit', 'plane', 'autonomous', 'fixed-wing'],

)
