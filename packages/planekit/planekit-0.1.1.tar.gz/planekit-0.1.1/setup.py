from distutils.core import setup
import setuptools


VERSION = "0.1.1"  # BURAYI AKLINIZDA TUTUN (Değiştirebilirsiniz)
long_description = ""
with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()
setup(
    name='planekit',
    packages=setuptools.find_packages(),
    install_requires=['pymavlink==2.4.29', 'pyserial==3.5'],
    version='0.1.1',
    license='MIT',
    description='Developer Tools for Fixed-wing',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Musa Şen',
    author_email='m42@gmail.com',
    url='https://github.com/msasen/planekit',

    download_url=f'https://github.com/msasen/planekit{VERSION}.tar.gz',
    keywords=['Planekit', 'plane', 'autonomous', 'fixed-wing'],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
