.. _installation:

Installation
============

PySnoop can be installed using pip or by cloning the repository.

Prerequisites
------------

- Python 3.7 or higher
- pip (Python package installer)
- Git (optional, for development)

Install via pip
--------------

.. code-block:: bash

    pip install pysnoop

Install from source
------------------

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/Nsfr750/pysnoop.git
       cd pysnoop

2. Install the package in development mode:

   .. code-block:: bash

       pip install -e .

   
   Or install with all development dependencies:
   
   .. code-block:: bash
   
       pip install -e ".[dev]"

Dependencies
------------

Required dependencies are automatically installed with the package. For development, additional dependencies can be found in ``requirements-dev.txt``.

Verification
-----------

To verify the installation, run:

.. code-block:: bash

    pysnoop --version

Troubleshooting
--------------

- **Permission Denied**: Use ``pip install --user pysnoop`` or run with administrator privileges.
- **Dependency Issues**: Ensure all system dependencies are installed.
- **Python Version**: Verify your Python version with ``python --version``.

For additional help, please refer to the :doc:`faq` or open an issue on GitHub.
