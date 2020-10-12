import logging
import traceback
import transaction
import ZPublisher.interfaces
import zope.component
import zExceptions.ExceptionFormatter

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
        if isinstance(req, WSGIRequest):
            # With WSGI, the error traceback itself no longer is printed to the
            # event.log, so we do that manually
            logger.exception(error_value)

        error_tb = '\n'.join(
            zExceptions.ExceptionFormatter.format_exception(
                error_type, error_value, error_tb,
                as_html=True,
            )
        )
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
        logger.warn(traceback.format_exc())
        logger.exception('Error while rendering error message')
        transaction.abort()
    else:  # no exception
        transaction.commit()


class PerFactException(Exception):
    ''' Special Exception Class
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
        - "args" (dictionary, default None which means {})
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

    def __init__(self, msg='', payload=None, **kw):
        super(PerFactUserWarning, self).__init__(
            msg=msg, show_to_user=True,
            appuserlog=False, payload=payload, **kw)
