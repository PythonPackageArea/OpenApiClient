from setuptools import find_packages, setup

setup(
    name="openapi_client",
    packages=find_packages(exclude=["tests"]),
    version="0.2.0",
    description="Продвинутый генератор Python-клиентов из OpenAPI спецификаций",
    author="lite",
    license="MIT",
    install_requires=[
        "jsonref>=1.0.0",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "simple-singleton>=1.0.0",
        "toml>=0.10.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "openapi-client = openapi_client.cli:generate",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
