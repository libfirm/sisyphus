.. Sisyphus documentation master file, created by
   sphinx-quickstart on Thu Mar 28 16:57:31 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Sisyphus's documentation!
====================================

Contents:

.. toctree::
   :maxdepth: 2

Introduction
============

Sisyphus is a tool/framework for creating automated testers.
The original problem we tried to solve was testing compilers:
A bunch of small testfiles should be compiled, linked and run, checking the compilation for warning and error messages and finally comparing the output of the produced executable against some reference output.
As similar requirements pop up in many projects we generalized and cleaned and some scripts we had written and release them as Sisyphus now.

Features
--------

Among the notable features of Sisyphus are:

- Clearly arranged text output
- Parallel test execution
- Read expected test outcomes
- Flexible foundation for configurations and variants.

By default Sisyphus tries to be brief in the information it displays.
Test status is color coded, expected test outcomes are hidden, the number of tests run is summarized.
Of course you can always increase the output verbosity to see more details of what is going on.

Parallel test execution allows you to fully utilize modern multi core machines and often dramatically improves test times compared to sequential testing.

Tracking test outcomes in exepctation files allow to track progress/regressions.
There are often cases where some tests are known to be defect but where you still want to detect failures in tests expected to be good.
This also allows to track progress and decling commits in a continuous integration scenario.

Finally once you start writing tests you often find yourself requiring more features/flexibility to achieve tasks or check properties you hadn't imagined before.
Sisyphus tries to be a flexible framework allowing you to write your own testing procedures in python.
It is up to you how much of the provided framework you use.

Anatomy of a Test
=================

A sphinx test is


Configuration Environments
==========================

A very common problem in testing is supporting multiple variants or configurations.
Sisyphus features an elaborate configuration management system to achieve this task.
This task is performed by the :py:class:Environment class.
The environment class behaves like a normal python dictionary object and allows you to set key/value pairs.
Additional field accesses are allowed as these often result in more intuitive/clear code.


Running Tests
=============



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

