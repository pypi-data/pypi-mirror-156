from setuptools import setup

name = "types-click-spinner"
description = "Typing stubs for click-spinner"
long_description = '''
## Typing stubs for click-spinner

This is a PEP 561 type stub package for the `click-spinner` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `click-spinner`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/click-spinner. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `634f18f615a93e826b253e261ca05f2c45ada134`.
'''.lstrip()

setup(name=name,
      version="0.1.12",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/click-spinner.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['click_spinner-stubs'],
      package_data={'click_spinner-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
