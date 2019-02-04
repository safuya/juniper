Juniper: Package lambda functions
=================================

Juniper is a packaging tool with a with a single purpose in mind: stream and standardize
the creation of a zip artifact for a set of AWS Lambda functions.

Packaging of python lambda functions is a problem a web developer faces when
building web APIs using AWS services. The main issue is that the dependencies
of the function must be included along with the business logic of the function.

This tool does **not** deploy or update a lambda function in AWS. This
tool is used to generate a set of .zip files contaning dependencies and
shared libraries, which you can use to deploy a lambda function.

Quickstart
**********

With Python==3.6 and Docker installed, install juniper:

.. code-block:: text

    > pip install juniper

Go to the code you are packaging and define a configuration for your
functions, ex in `manifest.yml`:

.. code-block:: yaml

    functions:
      router:            # Name of the lambda function (result in router.zip artifact)
        requirements: ./src/router/requirements.txt.  # Path to reqs file
        include:
        - ./src/commonlib/mylib                     # Include this in the zip
        - ./src/router_function/router              # Include this in the zip

Build it!

.. code-block:: text

    > juni build

Your .zip is now in the `dist/` directory.  🎉

juni build
**********

After installing juniper, and writing you manifest file, in its most basic form
`juni build` does the following:

* By default looks for a file called **manifest.yml**
* It outputs the .zip artifacts into a folder called **./dist**

These default values can be configured. To set the path of the manifest use:

    > juni build -m ./my_manifest_definition.yml

To update the output directory of the artifacts. Include the following section
in the manifest file:

.. code-block:: yaml

    package:
      output: ./build

    functions:
      router:
        requirements: ./src/router/requirements.txt.  # Path to reqs file
        include:
          - ./src/router_function/router              # Include this in the zip

In this case, the artifacts will be stored in a `./build` directory.

Features
********

This list defines the entire scope of Juniper. Nothing more, nothing else.

* Minimal manifest file to define packaging
* Using docker containers as a way to install dependencies and generate the artifacts
* Ability to tailor the requirements.txt per lambda
* Create an individual zip artifact for multiple lambda functions
* Ability to include shared dependencies (python modules relative to the function
  being packaged)

Contributing
************

For guidance on setting up a development environment and how to make a
contribution to Juniper, see the `contributing guidelines`_.

.. _contributing guidelines: https://github.com/eabglobal/juniper/blob/master/CONTRIBUTING.rst

Links
*****

* Documentation: https://eabglobal.github.io/juniper/
* License: `Apache Software License`_

* Code: https://github.com/eabglobal/juniper
* Issue tracker: https://github.com/eabglobal/juniper/issues
* Test status:

  * Linux, Mac: https://circleci.com/gh/eabglobal/juniper

.. _Apache Software License: https://github.com/eabglobal/juniper/blob/master/LICENSE
