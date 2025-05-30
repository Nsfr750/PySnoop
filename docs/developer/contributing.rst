.. _contributing:

Contributing to PySnoop
======================

We welcome contributions from the community! Here's how you can help:

Getting Started
--------------

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Run the tests
6. Submit a pull request

Development Setup
----------------

1. Create a virtual environment:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install development dependencies:

   .. code-block:: bash

       pip install -e ".[dev]"

Coding Standards
----------------

- Follow PEP 8 style guide
- Use type hints for all new code
- Write docstrings for all public functions and classes
- Keep lines under 100 characters

Testing
-------

Run the test suite with:

.. code-block:: bash

    pytest

Documentation
------------

To build the documentation locally:

.. code-block:: bash

    cd docs
    make html

The documentation will be available in ``http://tuxxle.ddns.net/pysnoop/docs/index.html``

Submitting Changes
-----------------

1. Write clear commit messages
2. Reference any related issues in your PR
3. Ensure all tests pass
4. Update documentation as needed

Code Review Process
------------------

1. Create a draft PR for early feedback
2. Request reviews from maintainers
3. Address all review comments
4. Once approved, a maintainer will merge your PR

Reporting Issues
---------------

When reporting issues, please include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Version information
- Any relevant error messages
