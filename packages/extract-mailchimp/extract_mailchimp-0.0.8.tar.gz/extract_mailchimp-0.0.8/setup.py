from setuptools import setup, find_packages

NAME = "extract_mailchimp"
VERSION = "0.0.8"

REQUIRES = [
    "python-dotenv==0.20.0",
    "mailchimp-marketing>=3.0.75",
    "certifi>=2017.4.17",
    "python-dateutil>=2.1",
    "requests>=2.23",
    "six>=1.10",
    "urllib3>=1.23",
]

setup(
    name=NAME,
    version=VERSION,
    description="Extract MailChimp data only by folder ID",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Eunbin Park",
    author_email="parkeb417@gmail.com",
    install_requires=REQUIRES,
    packages=find_packages(),
    keywords=["data", "api", "mailchimp"],
    python_requires=">=3.6",
    include_package_data=True,
)