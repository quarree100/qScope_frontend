Usage
=====
About the user interface frontend of the Q-Scope

Modes
^^^^^
Q-Scope runs at different machine states:


.. _input_mode:

Input_Mode
----------
In the Input Mode, users can set household-, buildings- global parameters. They can leave the mode placing a token on the "simulation mode" selector.

.. _data_view:

Data View
---------
The Data View starts after finishing of a simulation. Here, aggregated values are shown in graphs as a f(t) and can be accessed interactively.

.. _simulation:

Simulation
----------
The Simulation can be started using ``S`` key. It will generate an experiment API file for GAMA according to this scheme: https://gama-platform.org/wiki/Headless#simulation-output and run the provided model file using the gama-headless.sh . These two files are to be set up in ``config.py``.