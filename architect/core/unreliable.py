# -*- coding: utf-8 -*-

from .log import error as _log_error


class Unreliable(object):
    @staticmethod
    def _defaultErrorHandler(err):
        # type: (Exception) -> None
        _log_error(unicode(err))
        import traceback
        traceback.print_exc()

    def __init__(self):
        self._errorHandler = Unreliable._defaultErrorHandler

    def onError(self, fn):
        self._errorHandler = fn

    def _handleError(self, err):
        try:
            self._errorHandler(err)
            return (None, err)
        except Exception as err:
            _log_error(unicode(err))
            return (None, err)

    def tryCall(self, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs), None
        except Exception as err:
            return self._handleError(err)
