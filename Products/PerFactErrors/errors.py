import logging
import transaction
import ZPublisher.interfaces
import zope.component
import zExceptions.ExceptionFormatter
from zExceptions import Unauthorized
from zope.pagetemplate.pagetemplate import PTRuntimeError

try:
    from ZPublisher.HTTPRequest import WSGIRequest
except ImportError:
    class WSGIRequest():
        pass

logger = logging.getLogger(__name__)


@zope.component.adapter(ZPublisher.interfaces.IPubFailure)
def afterfail_error_message(event):
    """
    Render error message after an aborted transaction.
    The transaction in which the exception was raised gets aborted just before
    IPubFailure, so we can safely commit a new one during our error handling
    procedure. This is also the reason why we cannot use a logging view
    directly.
    """
    req = event.request
    context = req['PARENTS'][0]
    render = getattr(context, 'afterfail_error_message_', None)
    if render is None:
        return
    try:
        error_type, error_value, error_tb = event.exc_info
        # With WSGI, the error traceback itself no longer is printed to the
        # event.log, so we do that manually - except for special cases
        log_error = (
            isinstance(req, WSGIRequest)
            and not isinstance(error_value, Unauthorized)
            and not (
                isinstance(error_value, PerFactException)
                and not error_value.apperrorlog
            )
        )
        if log_error:
            logger.exception(error_value)

        error_tb = '\n'.join(
            zExceptions.ExceptionFormatter.format_exception(
                error_type, error_value, error_tb,
                as_html=True,
            )
        )

        # Chameleon adds some traceback information to the error_value's
        # __str__ method, which we do not want to show the user, so we replace
        # the error value by its original string representation. Information
        # like the exact line and expression in the page template can still be
        # found in the event.log and in the traceback.
        if hasattr(error_value, '_original__str__'):
            error_value = error_value._original__str__()

        # Chameleon's own errors are also too verbose
        if isinstance(error_value, PTRuntimeError):
            error_value = 'Error parsing page template'

        # Inside a method inside Zope, we can handle a string better, so we
        # pass the __name__ as error_type
        body = render(
            error_type=error_type.__name__,
            error_value=error_value,
            error_tb=error_tb,
        )
        if body is not None:
            req.response.setBody(body)
    except Exception:
        logger.exception('Error while rendering error message')
        transaction.abort()
    else:  # no exception
        transaction.commit()


class PerFactException(Exception):
    '''
    This special exception class may be used for equipping error
    messages with dynamic content where it is possible to keep the
    parts separate from the error message.
    Also additional properties allow more control in error handling.
    '''

    def __init__(self, msg='', show_to_user=False,
                 apperrorlog=False, payload=None, **kw):
        '''
        Input:
        - "msg" (string) is the error message,
          possibly containing placeholders like "{lotnumber}"
        - "show_to_user" (boolean, default False), controls
          if the error is intended to be shown to the end
          user even on a production system. Also causes the
          error to be translated before showing it to the user
          (not the one that is inserted into the database). If
          it is not set, the user simply gets a generic "An
          error occured" with an ID.
        - "apperrorlog" (boolean, default True), controls if
          the error is logged in the apperrorlog
        - "payload" (dictionary, default None which means {})
          contains values that should be inserted into the
          placeholders, possibly after translation.
        - **kw should be used to allow more arguments to be
          passed later. Anything given here should be stored in
          the class instance.
        '''

        super(PerFactException, self).__init__()
        self.msg = msg
        self.show_to_user = show_to_user
        self.apperrorlog = apperrorlog
        self.payload = payload or {}

    def __str__(self):
        return repr((self.msg, self.payload))


class PerFactUserWarning(PerFactException):
    '''
    This subclass of PerFactException automatically sets some
    superclasses properties when initiallized. In case of this
    subclass, the exception shall not by logged and the rendered
    error message shall be displayed to the user.
    '''

    def __init__(self, msg='', payload=None, **kw):
        super(PerFactUserWarning, self).__init__(
            msg=msg, show_to_user=True,
            appuserlog=False, payload=payload, **kw)
