from requests import get
import setuptools

REPOSITORY = "https://github.com/agzg/ghicon/releases/latest"
version = get(REPOSITORY).url.split("/")[-1]

with open("README.md", "r") as f:
	long_description = f.read()
	
setuptools.setup(
	name="ghicon",
	packages=setuptools.find_packages(),
	version="0.0.1",
	license="MIT",
	description="GitHubesque identicon generator.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	author="Ali Azam",
	author_email="azam.vw@gmail.com",
	url="https://github.com/agzg/ghicon",
	download_url=f"{REPOSITORY}/archive/refs/tags/{version}.tar.gz",
	keywords=["identicon", "generator", "github", "pillow", "icon"],
	install_requires=["pillow", "requests"],
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python"
	],
)

