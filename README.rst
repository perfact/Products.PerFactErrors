======================
Products.PerFactErrors
======================

This package provides a basic implementation of error views for Zope 4.

NotFound
========

The is a template in ``Products.PerfactErrors.notfound.pt`` which is rendered
in case of a HTTP-404.

Unauthorized / Forbidden
========================

For those errors a redirect to the root of the website is performed.

Other Exceptions
================

All other exceptions are logged via a ``LoggingView`` which can be subclassed and configured to log to a specific target.
