from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="svector-sdk",
    version="1.3.1",
    author="SVECTOR Team",
    author_email="support@svector.co.in",
    description="Official Python SDK for SVECTOR's AI models - Spec-3, Theta-35, and advanced reasoning systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/svector-corporation/svector-python",
    project_urls={
        "Bug Tracker": "https://github.com/svector-corporation/svector-python/issues",
        "Documentation": "https://platform.svector.co.in",
        "Homepage": "https://www.svector.co.in",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="svector ai machine-learning llm spec-chat artificial-intelligence conversational-ai language-models",
    entry_points={
        "console_scripts": [
            "svector=svector.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
