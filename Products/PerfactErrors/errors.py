import OFS.interfaces
import ZPublisher.interfaces
import logging
import transaction
import zExceptions
import zope.cachedescriptors.property
import zope.component

log = logging.getLogger(__name__)


try:
    from perfact.generic import get_uuid4 as uuid4
except ImportError:
    log.warn('perfact.generic not found, fallback to uuid.uuid4')
    from uuid import uuid4


class RedirectView(object):
    """Redirects in case of error."""

    def __call__(self):
        log.warn('Redirecting to root')
        base_url = self.request.base
        raise zExceptions.Redirect(base_url)


class UnauthorizedRedirectView(RedirectView):
    """Redirects except for ZMI toplevel."""

    @property
    def no_redirect(self):
        """Do not redirect at toplevel for manage and manage_main.

        This allows to login via basic auth for managers.
        """
        auth_methods = ['manage', 'manage_main']

        is_toplevel = OFS.interfaces.IApplication.providedBy(self.__parent__)
        if is_toplevel:
            # Last component of the URL:
            url = self.request.URL
            last_url_part = url.rsplit('/', 1)[1]
            if last_url_part in auth_methods:
                return True

    def __call__(self):
        if self.no_redirect:
            return
        else:
            super(UnauthorizedRedirectView, self).__call__()


class DummyView(object):
    """We need this view to prohibit the re-raise of exceptions.

    In case no exception view is registered, the exception will be re-raised
    and there will be no possibility to influence the body of the response.

    see ZPublisher.WSGIPublisher.transaction_pubevents

    """

    def __call__(self,):
        """Provide dummy callable."""


class LoggingView(object):
    """Log the error and traceback and render a standard error message."""

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request

    def log_traceback(self):
        log.error('Logging internal server error on %s with UUID: %s',
                  self.request.other['URL'], self.uuid, exc_info=True)
        log.error('Environment: %s', self.request.environ)

    @zope.cachedescriptors.property.Lazy
    def uuid(self):
        return uuid4()

    def __call__(self):
        """Log the error and render standard error message."""
        self.log_traceback()
        root = self.request['PARENTS'][-1]
        if not hasattr(root, 'standard_error_message_show'):
            return ''
        std_err_mess = root.standard_error_message_show
        result = std_err_mess(uuid=self.uuid)
        # Commit the results of our error handling procedure.
        transaction.commit()
        return result


@zope.component.adapter(ZPublisher.interfaces.IPubFailure)
def log_and_render_error_message(event):
    """Log and render exception view after an aborted transaction."""
    # The transaction in which the exception was raised gets aborted just
    # before IPubFailure, so we can safely commit a new one during our error
    # handling procedure. This is also the reason, why we cannot use a logging
    # view directly.
    view = LoggingView(request=event.request)
    event.request.response.setBody(view())
