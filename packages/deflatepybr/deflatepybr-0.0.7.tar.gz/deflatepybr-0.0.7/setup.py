import setuptools

long_description = open("README.md").read()

project_urls = {"Github": "https://github.com/eugeniothiago/deflatepy"}

setuptools.setup(
    name="deflatepybr",
    version="0.0.7",
    author="Thiago Eugênio",
    description="A simple package to deflate BR currency values using IPCA's historical yearly and monthly indexes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls=project_urls,
    packages=["deflator"],
    readme="README.md",
    install_requires=["requests", "pandas"],
)
