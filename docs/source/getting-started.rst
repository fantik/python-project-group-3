Getting Started
===============

This project uses `uv` for dependency management and command execution.

Install dependencies
--------------------

.. code-block:: bash

   uv sync

Run the application
-------------------

.. code-block:: bash

   uv run python main.py

Run tests
---------

.. code-block:: bash

   uv run python -m unittest discover -s tests

Build documentation
-------------------

.. code-block:: bash

   uv sync --group docs
   LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 uv run --group docs sphinx-build -b html docs/source docs/build/html
