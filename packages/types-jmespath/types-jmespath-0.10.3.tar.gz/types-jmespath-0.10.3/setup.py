from setuptools import setup

name = "types-jmespath"
description = "Typing stubs for jmespath"
long_description = '''
## Typing stubs for jmespath

This is a PEP 561 type stub package for the `jmespath` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `jmespath`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/jmespath. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `634f18f615a93e826b253e261ca05f2c45ada134`.
'''.lstrip()

setup(name=name,
      version="0.10.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/jmespath.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['jmespath-stubs'],
      package_data={'jmespath-stubs': ['__init__.pyi', 'ast.pyi', 'exceptions.pyi', 'functions.pyi', 'lexer.pyi', 'parser.pyi', 'visitor.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
