Getting Started
===============

This project uses `uv` for dependency management and command execution.

Install uv
----------

Use Homebrew on **macOS / Linux**:

If you do not have Homebrew yet, install it from the
`Homebrew installation guide <https://brew.sh/>`_.

.. code-block:: bash

   brew install uv

Use Chocolatey on **Windows**:

If you do not have Chocolatey yet, install it from the
`Chocolatey installation guide <https://chocolatey.org/install>`_.

.. code-block:: powershell

   choco install uv

Or use WinGet on **Windows**:

If you do not have WinGet yet, see the
`Microsoft WinGet installation guide <https://learn.microsoft.com/en-us/windows/package-manager/winget/>`_.

.. code-block:: powershell

   winget install --id=astral-sh.uv -e

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
