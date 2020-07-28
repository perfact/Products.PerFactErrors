import six
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
            # Actually, the test should be for "Are we using WSGI", not "Are we
            # using Python 3". Not sure how to test that.

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
        logger.exception('Error while rendering error message')
        transaction.abort()
    else:  # no exception
        transaction.commit()
