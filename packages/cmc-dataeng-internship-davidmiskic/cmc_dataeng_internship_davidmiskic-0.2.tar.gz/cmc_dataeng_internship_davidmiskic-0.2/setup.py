from setuptools import setup, find_packages


setup(
    name='cmc_dataeng_internship_davidmiskic',
    version='0.2',
    license='MIT',
    author="David Miškić",
    packages=find_packages('src'),
    package_dir={'': 'src'},
)