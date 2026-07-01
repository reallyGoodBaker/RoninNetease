from .basic import clientApi, serverApi, isServer, __modname__

__all__ = [
    'Asset',
]

__prefix = __modname__ + '.assets.'


def _loadFromAssets(uri):
    api = serverApi if isServer() else clientApi
    try:
        m = api.ImportModule(__prefix + uri).__dict__
        defaultAsset = m.get('Asset', {})
        assembled = defaultAsset.update(m)
        return assembled
    except Exception:
        return None

class Asset(object):
    cached = {} # type: dict[str, Asset]

    def __init__(self, uri):
        # type: (str) -> None
        self.uri = uri

    def load(self, useCache=False):
        uri = self.uri
        if useCache and uri in Asset.cached:
            return Asset.cached[uri]
        _asset = _loadFromAssets(uri)
        if useCache and _asset is not None:
            Asset.cached[uri] = _asset
        return _asset

    @staticmethod
    def reach(uri):
        return _loadFromAssets(uri)