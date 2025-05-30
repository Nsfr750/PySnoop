.. _quickstart:

Quick Start Guide
================

This guide will help you get started with PySnoop quickly.

Launching the Application
-------------------------

After installation, you can launch PySnoop from the command line:

.. code-block:: bash

    pysnoop

Or if you installed in development mode:

.. code-block:: bash

    python -m pysnoop

Connecting a Card Reader
----------------------

1. Connect your magnetic stripe card reader to your computer.
2. Ensure the reader is properly recognized by your operating system.
3. In PySnoop, select the correct COM port from the dropdown menu.
4. Click "Initialize Reader" to establish the connection.

Reading a Card
-------------

1. Insert a magnetic stripe card into the reader.
2. Click the "Read Card" button in the PySnoop interface.
3. The card data will be displayed in the main window.

Validating Card Numbers
----------------------

1. Go to the "C10 Validator" tab.
2. Enter a card number in the input field.
3. Click "Validate C10" to check if the number is valid.
4. The result will be displayed below the input field.

Managing Card Database
---------------------

1. To save a card to the database, read a card and click "Save to Database".
2. View saved cards in the "Database" tab.
3. Export card data using the "Export" button (supports JSON and CSV formats).

Troubleshooting
--------------

- **Card Not Reading**: Ensure the card is properly inserted and the reader is connected.
- **Connection Issues**: Try a different USB port or check device manager for conflicts.
- **Validation Errors**: Check that the card number is entered correctly.

For more detailed information, please refer to the :doc:`user/interface` guide.
