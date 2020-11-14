import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lw-trv-proxy",
    version="0.6.2",
    author="Colin Robbins",
    author_email="colin.john.robbins@gmail.com",
    description="A Lightwave RF Proxy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ColinRobbins/Homeassistant-Lightwave-TRV",
    entry_points = {
        'console_scripts': ['lwproxy=lwproxy.lwproxy:main']
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
