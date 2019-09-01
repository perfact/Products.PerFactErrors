======================
Products.PerFactErrors
======================

This package provides a basic implementation of error handling in Zope 4 using
a ``standard_error_message`` method in the ZODB, similar to Zope 2.

The key is to subscribe a method to ``ZPublisher.interfaces.IPubFailure``,
which is thrown after the actual transaction aborted. This allows the error
handling procedure to interact with the database and eventually commit a
transaction.
