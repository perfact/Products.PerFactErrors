======================
Products.PerFactErrors
======================

This package provides error handling in a second transaction after the doomed
transaction was already rolled back, but within the same request.

It subscribes a method to ``ZPublisher.interfaces.IPubFailure``,
which is thrown after the actual transaction aborted. This allows the error
handling procedure to interact with the database and eventually commit a
transaction.

Usage
=====

To implement an error handling procedure that is executed after the failed
transaction is already rolled back, place a method named
``afterfail_error_message_`` so it is found in the context of where the error
occurs. Additionally, you should have a ``standard_error_message``, especially
under Zope 4, where otherwise a default error view is called after the handler
and overwrites the output.

Within the doomed transaction, ``standard_error_message`` is called and its
result is used for the response of the request by default. After the
transaction is rolled back, ``afterfail_error_message_`` is called with the
same arguments (``error_type``, ``error_value`` and ``error_tb``) in a new
transaction, which is afterwards commited unless an uncaught exception occurs
inside the method.  If the method returns a string, this replaces the response.
If it returns ``None``, the original response from ``standard_error_message``
is used.
