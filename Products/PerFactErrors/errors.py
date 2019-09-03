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
    render = getattr(context, 'perfact_error_handler_', None)
    if render is None:
        return
    try:
        error_type, error_value, error_tb = event.exc_info
        body = render(
            error_type=error_type,
            error_value=error_value,
            error_tb=error_tb,
        )
        if body is not None:
            req.response.setBody(body)
    except Exception:
        logger.warn('Error while rendering error message')
        traceback.print_exc()

        transaction.abort()
    else:  # no exception
        transaction.commit()
