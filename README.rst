======================
Products.PerFactErrors
======================

This package provides a basic implementation of error views for Zope 4.

NotFound
========

The is a template in ``Products.PerFactErrors.notfound.pt`` which is rendered
in case of a HTTP-404.

Unauthorized / Forbidden
========================

For those errors a redirect to the root of the website is performed.

``Unauthorized`` is not redirected for ``/manage`` and ``/manage_main`` on root
level.

Other Exceptions
================

All other exceptions are logged via a ``LoggingView`` which is actually called
in a subscriber to ``ZPublisher.interfaces.IPubFailure`` as we have already
aborted the initial transaction of the request at this point. This allows the
error handling procedure to interact with the database and eventually commit a
transaction.
