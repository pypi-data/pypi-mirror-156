import os
from distutils.core import setup

message = "This is not the package you want. Contact #supercomputing team for more information."

allow_setup = bool(os.environ.get("OPENAI_DUMMY_PACKAGE_BUILD", False))
if not allow_setup:
    raise Exception(message)

setup(
    name=os.environ["DUMMY_PACKAGE_NAME"],
    version=os.environ["VERSION"],
    url="https://openai.com",
    author="OpenAI",
    author_email="supercomputing@openai.com",
)
