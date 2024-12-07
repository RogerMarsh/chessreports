# __init__.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide row definition to various file formats.

The database interface defined in the core.database.Database and
core.cursor.Cursor classes is used.

Access is provided for:

dBaseIII databases
CSV files
Text files
zip compressed text files
bz2 compressed text files

The text file formats are treated as "one line" is "one record".

"""
