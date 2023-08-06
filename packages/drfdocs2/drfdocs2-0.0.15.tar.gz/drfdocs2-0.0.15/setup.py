from setuptools import find_packages, setup

setup(
    name="drfdocs2",
    version=__import__('rest_framework_docs').__version__,
    author="Pavlo Komarov",
    author_email="pavlo.komarov@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    url="http://www.drfdocs.com",
    license='BSD',
    description="Documentation for Web APIs made with Django 3.0 & 4.0 and DRF",
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
