import logging
import traceback
import transaction
import ZPublisher.interfaces
import zope.component

logger = logging.getLogger(__name__)


@zope.component.adapter(ZPublisher.interfaces.IPubFailure)
def standard_error_message(event):
    """Render error message after an aborted transaction."""
    # The transaction in which the exception was raised gets aborted just
    # before IPubFailure, so we can safely commit a new one during our error
    # handling procedure. This is also the reason why we cannot use a logging
    # view directly.
    req = event.request
    context = req['PARENTS'][0]
    render = getattr(context, 'perfact_error_handler', None)
    if render is None:
        return
    try:
        exc = event.exc_info
        req.response.setBody(render(
            error_type=exc[0],
            error_value=exc[1],
            error_tb=exc[2],
        ))
    except Exception:
        logger.warn('Error while rendering error message')
        for item in traceback.format_tb():
            logger.warn(item)

        transaction.abort()
    else:  # no exception
        transaction.commit()
