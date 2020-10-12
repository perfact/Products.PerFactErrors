from Products.PythonScripts.Utility import allow_module, allow_class
from .errors import PerFactException, PerFactUserWarning

allow_module("Products.PerFactErrors")

allow_class(PerFactException)
allow_class(PerFactUserWarning)
