from setuptools import setup

setup(
        name="keithley-teng",
        version="0.1",
        description="Utility for measuring TENG-sensor output with a Keithley 2600B SMU",

        author="Matthias Quintern",
        author_email="matthias.quintern@tum.de",

        url="https://git.quintern.xyz/MatthiasQuintern/teng-measurement.git",

        license="GPLv3",

        packages=["keithley-teng"],
        # packages=setuptools.find_packages(),
        install_requires=["pyvisa", "pyvisa-py"],

        classifiers=[
            "Programming Language :: Python :: 3",
            ],

        # entry_points={
        #     "console_scripts": [ "teng=teng.interactive:main" ],
        #     },
)


