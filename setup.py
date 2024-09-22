from setuptools import find_packages, setup

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="loki-logging-handler",
    version="0.0.5",
    author="Eric Fu",
    description="Logging handler to send logs to Grafana Loki",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuyufjh/loki_logging_handler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="loki, logging, handler",
    install_requires=["requests==2.28.2"],
    test_suite="tests",
    license="MIT",
    python_requires=">=3.6",
)
