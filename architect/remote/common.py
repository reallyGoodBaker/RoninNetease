from ..core.basic import isServer
from ..core.scheduler import Future
from ..level.server import LevelServer
from ..level.client import LevelClient
from ..core.annotation import AnnotationHelper

if 1 > 2:
    from ..core.subsystem import SubsystemManager


REMOTE_CALL_KEY = '[[remote_call]]'
REMOTE_RET_KEY = '[[remote_ret]]'
REMOTE_INNER_KEY = '[[remote_inner]]'


def Remote(method):
    AnnotationHelper.addAnnotation(method, REMOTE_INNER_KEY, True)
    return method


def record():
    return _serverRemoteMethods if isServer() else _clientRemoteMethods


_clientRemoteMethods = {}
_serverRemoteMethods = {}


def _createCallData(id, uri, *args, **kwargs):
    return {
        'id': id,
        'uri': uri,
        'args': args,
        'kwargs': kwargs,
        'requireReturn': False
    }

def _createInvokeData(id, uri, *args, **kwargs):
    return {
        'id': id,
        'uri': uri,
        'args': args,
        'kwargs': kwargs,
        'requireReturn': True
    }


def _callRemoteMethod(subsys, data):
    id = data['id']
    uri = data['uri']
    args = data['args']
    kwargs = data['kwargs']
    requireReturn = data['requireReturn']
    result = None
    err = None

    try:
        if isServer():
            result = _serverRemoteMethods[uri](data['__id__'], *args, **kwargs)
        else:
            result = _clientRemoteMethods[uri](*args, **kwargs)
    except Exception as e:
        err = e
        import traceback
        print('[ERROR] Remote call failed: \n' + traceback.format_exc())

    if requireReturn:
        def _sendReturn(result, err, id=id):
            returnVal = {
                'result': result,
                'err': err,
                'id': id
            }
            if isServer():
                # 客户端发送的rpc
                subsys.sendClient(data['__id__'], REMOTE_RET_KEY, returnVal)
            else:
                # 服务器发送的rpc
                subsys.sendServer(REMOTE_RET_KEY, returnVal)
        if isinstance(result, Future):
            result.done(lambda v: _sendReturn(v, None))
            result.expected(lambda e: _sendReturn(None, e))
        else:
            _sendReturn(result, err)


_clientRets = {}
_serverRets = {}


def _registerRemoteCalls(sysManager):
    # type: (SubsystemManager) -> None
    def _handleCall(ev):
        uri = ev['uri']
        sysName = uri.split('.')[0]
        _callRemoteMethod(sysManager.getSubsystem(sysName), ev)

    sysManager.addListener(
        REMOTE_CALL_KEY,
        _handleCall,
        True
    )

    def _handleRecev(ev):
        rets = _serverRets if isServer() else _clientRets
        retHandler = rets.get(ev['id'])
        if not retHandler:
            return
        retHandler(ev['result'], ev['err'])
        del rets[ev['id']]

    sysManager.addListener(
        REMOTE_RET_KEY,
        _handleRecev,
        True
    )


class _RemoteClient(object):
    _rpcId = 0

    def __init__(self):
        from ..core.subsystem import subsystem
        self.subsys = subsystem

    def accId(self):
        _id = _RemoteClient._rpcId
        _RemoteClient._rpcId += 1
        return _id

    def call(self, uri, *args, **kwargs):
        self.subsys.sendServer(
            REMOTE_CALL_KEY,
            _createCallData(self.accId(), uri, *args, **kwargs)
        )

    def invoke(self, uri, *args, **kwargs):
        ftr, resolve, reject = Future.resolvers()
        retId = self.accId()
        self.subsys.sendServer(
            REMOTE_CALL_KEY,
            _createInvokeData(retId, uri, *args, **kwargs)
        )
        def _timeout():
            del _clientRets[retId]
            reject('timeout')
        timer = LevelClient.getInstance().game.AddTimer(3, _timeout)

        def _recieveReturn(result, err):
            LevelClient.getInstance().game.CancelTimer(timer)
            if err:
                return reject(err)
            return resolve(result)
        _clientRets[retId] = _recieveReturn

        return ftr
    

class _RemoteServer(object):
    _rpcId = 0

    def __init__(self):
        from ..core.subsystem import subsystem
        self.subsys = subsystem

    def accId(self):
        _id = _RemoteServer._rpcId
        _RemoteServer._rpcId += 1
        return _id

    def call(self, id, uri, *args, **kwargs):
        self.subsys.sendClient(
            id,
            REMOTE_CALL_KEY,
            _createCallData(self.accId(), uri, *args, **kwargs)
        )

    def invoke(self, id, uri, *args, **kwargs):
        ftr, resolve, reject = Future.resolvers()
        retId = self.accId()
        self.subsys.sendClient(
            id,
            REMOTE_CALL_KEY,
            _createInvokeData(retId, uri, *args, **kwargs)
        )

        def _timeout():
            del _serverRets[retId]
            reject('timeout')

        timer = LevelServer.game.AddTimer(3, _timeout)

        def _recieveReturn(result, err):
            LevelServer.game.CancelTimer(timer)
            if err:
                return reject(err)
            return resolve(result)
        _serverRets[retId] = _recieveReturn

        return ftr

_remoteClient = _RemoteClient()
_remoteServer = _RemoteServer()

def getRemote():
    return _remoteServer if isServer() else _remoteClient

class remote:
    client = _remoteClient
    server = _remoteServer