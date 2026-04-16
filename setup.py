#!/usr/bin/env python3
"""Setup configuration for Trading MVP package installation."""

from setuptools import setup, find_packages

setup(
    name="trading-mvp",
    version="0.3.5",
    description="Plataforma de Trading Autónomo con Multi-Agentes LLM",
    author="Diego Velez",
    packages=find_packages(),
    install_requires=[
        'alpaca-py>=0.1.0',
        'google-genai>=1.0.0',
        'python-dotenv>=1.0.0',
        'pytz>=2023.0',
        'psycopg2-binary>=2.9.0',
        'supabase>=2.0.0',
        'requests>=2.32.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'python-dateutil>=2.8.0',
    ],
    python_requires='>=3.10',
    include_package_data=True,
    zip_safe=False,
)