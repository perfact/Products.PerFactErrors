23.1.0
======

- Also render exception causes according to 
  [PEP 3134](https://peps.python.org/pep-3134/#explicit-exception-chaining)

23.0.0
======

- Fix ``PerFactException`` handling for Chameleon-based page templates.

22.2.0
======

- Fix parameter in ``PerFactUserWarning`` so these are not included in the
  error log.

- Adjust version numbering

0.8
===

- Reduce overly verbose error output that is added by Chameleon if an error
  occurs in a Page Template

0.7
===

- Do not log certain error types
  (`#3 <https://github.com/perfact/Products.PerFactErrors/pull/3>`_)
