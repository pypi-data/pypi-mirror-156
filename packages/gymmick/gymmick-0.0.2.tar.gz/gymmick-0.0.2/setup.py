from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='gymmick',
    version='0.0.2',
    description='Simple functionality for the creation of visuals-based OpenAI Gym environments.',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Abhay Raj',
    keywords=['Gym', 'OpenAI', 'Environment', 'ReinforcementLearning'],
    url='https://github.com/GithubDev939/gymmick',
    download_url='https://pypi.org/project/gymmick/'
)

install_requires = [
    'pygame',
    'numpy',
    'gym'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
