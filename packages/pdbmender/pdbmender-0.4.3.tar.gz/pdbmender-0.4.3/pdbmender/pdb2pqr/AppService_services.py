##################################################
# ./AppService_services.py
# generated by ZSI.wsdl2python
#
#
##################################################


from AppService_services_types import *
from AppService_services_types import nbcr_sdsc_edu_opal_types as ns1
import urlparse, types
from ZSI.TCcompound import Struct
from ZSI import client
import ZSI


class AppServiceInterface:
    def getAppServicePortType(self, portAddress=None, **kw):
        raise NonImplementationError, "method not implemented"


class AppServiceLocator(AppServiceInterface):
    AppServicePortType_address = (
        "http://ws.nbcr.net:8080/axis-1.2.1/services/Pdb2pqrOpalService"
    )

    def getAppServicePortTypeAddress(self):
        return AppServiceLocator.AppServicePortType_address

    def getAppServicePortType(self, portAddress=None, **kw):
        return AppServicePortSoapBindingSOAP(
            portAddress or AppServiceLocator.AppServicePortType_address, **kw
        )


class AppServicePortSoapBindingSOAP:
    def __init__(self, addr, **kw):
        netloc = (urlparse.urlparse(addr)[1]).split(":") + [
            80,
        ]
        if not kw.has_key("host"):
            kw["host"] = netloc[0]
        if not kw.has_key("port"):
            kw["port"] = int(netloc[1])
        if not kw.has_key("url"):
            kw["url"] = urlparse.urlparse(addr)[2]
        self.binding = client.Binding(**kw)

    def destroy(self, request):
        """
        @param: request is str

        @return: response from destroyResponse::
            _destroyOutput: ns1.StatusOutputType_Def
              _baseURL: str
              _code: int
              _message: str
        """

        if not isinstance(request, basestring):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {"requestclass": destroyRequestWrapper}
        response = self.binding.Send(
            None, None, request, soapaction="http://nbcr.sdsc.edu/opal/destroy", **kw
        )
        response = self.binding.Receive(destroyResponseWrapper())

        if not isinstance(response, destroyResponse) and not issubclass(
            destroyResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def getAppConfig(self, request):
        """
        @param: request to getAppConfigRequest::
            _getAppConfigInput: ns1.AppConfigInputType_Def

        @return: response from getAppConfigResponse::
            _getAppConfigOutput: ns1.AppConfigType_Def
              _binaryLocation: str
              _defaultArgs: str, optional
              _metadata: ns1.AppMetadataType_Def
                _info: str, optional
                _types: ns1.ArgumentsType_Def, optional
                  _flags: ns1.FlagsArrayType_Def, optional
                    _flag: ns1.FlagsType_Def, optional
                      _id: str
                      _tag: str
                      _textDesc: str, optional
                  _implicitParams: ns1.ImplicitParamsArrayType_Def, optional
                    _param: ns1.ImplicitParamsType_Def, optional
                      _extension: str, optional
                      _id: str
                      _ioType: ns1.IOType_Def
                        _IOType: str, optional
                      _max: int, optional
                      _min: int, optional
                      _name: str, optional
                      _required: boolean, optional
                      _semanticType: str, optional
                      _textDesc: str, optional
                  _taggedParams: ns1.ParamsArrayType_Def, optional
                    _param: ns1.ParamsType_Def, optional
                      _id: str
                      _ioType: ns1.IOType_Def, optional
                      _paramType: ns1.ParamType_Def
                        _ParamType: str, optional
                      _required: boolean, optional
                      _semanticType: str, optional
                      _tag: str, optional
                      _textDesc: str, optional
                      _value: str, optional
                    _separator: str, optional
                  _untaggedParams: ns1.ParamsArrayType_Def, optional
                _usage: str
              _parallel: boolean
        """

        if not isinstance(request, getAppConfigRequest) and not issubclass(
            getAppConfigRequest, request.__class__
        ):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        response = self.binding.Send(
            None,
            None,
            request,
            soapaction="http://nbcr.sdsc.edu/opal/getAppConfig",
            **kw
        )
        response = self.binding.Receive(getAppConfigResponseWrapper())

        if not isinstance(response, getAppConfigResponse) and not issubclass(
            getAppConfigResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def getAppMetadata(self, request):
        """
        @param: request to getAppMetadataRequest::
            _getAppMetadataInput: ns1.AppMetadataInputType_Def

        @return: response from getAppMetadataResponse::
            _getAppMetadataOutput: ns1.AppMetadataType_Def
              _info: str, optional
              _types: ns1.ArgumentsType_Def, optional
                _flags: ns1.FlagsArrayType_Def, optional
                  _flag: ns1.FlagsType_Def, optional
                    _id: str
                    _tag: str
                    _textDesc: str, optional
                _implicitParams: ns1.ImplicitParamsArrayType_Def, optional
                  _param: ns1.ImplicitParamsType_Def, optional
                    _extension: str, optional
                    _id: str
                    _ioType: ns1.IOType_Def
                      _IOType: str, optional
                    _max: int, optional
                    _min: int, optional
                    _name: str, optional
                    _required: boolean, optional
                    _semanticType: str, optional
                    _textDesc: str, optional
                _taggedParams: ns1.ParamsArrayType_Def, optional
                  _param: ns1.ParamsType_Def, optional
                    _id: str
                    _ioType: ns1.IOType_Def, optional
                    _paramType: ns1.ParamType_Def
                      _ParamType: str, optional
                    _required: boolean, optional
                    _semanticType: str, optional
                    _tag: str, optional
                    _textDesc: str, optional
                    _value: str, optional
                  _separator: str, optional
                _untaggedParams: ns1.ParamsArrayType_Def, optional
              _usage: str
        """

        if not isinstance(request, getAppMetadataRequest) and not issubclass(
            getAppMetadataRequest, request.__class__
        ):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        response = self.binding.Send(
            None,
            None,
            request,
            soapaction="http://nbcr.sdsc.edu/opal/getAppMetadata",
            **kw
        )
        response = self.binding.Receive(getAppMetadataResponseWrapper())

        if not isinstance(response, getAppMetadataResponse) and not issubclass(
            getAppMetadataResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def getOutputAsBase64ByName(self, request):
        """
        @param: request to getOutputAsBase64ByNameRequest::
            _getOutputAsBase64ByNameInput: ns1.OutputsByNameInputType_Def
              _fileName: str
              _jobID: str

        @return: response from getOutputAsBase64ByNameResponse::
            _item: str, optional
        """

        if not isinstance(request, getOutputAsBase64ByNameRequest) and not issubclass(
            getOutputAsBase64ByNameRequest, request.__class__
        ):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        response = self.binding.Send(
            None,
            None,
            request,
            soapaction="http://nbcr.sdsc.edu/opal/getOutputAsBase64ByName",
            **kw
        )
        response = self.binding.Receive(getOutputAsBase64ByNameResponseWrapper())

        if not isinstance(response, getOutputAsBase64ByNameResponse) and not issubclass(
            getOutputAsBase64ByNameResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def getOutputs(self, request):
        """
        @param: request is str

        @return: response from getOutputsResponse::
            _getOutputsOutput: ns1.JobOutputType_Def
              _outputFile: ns1.OutputFileType_Def, optional
                _name: str
                _url: str
              _stdErr: str, optional
              _stdOut: str, optional
        """

        if not isinstance(request, basestring):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {"requestclass": getOutputsRequestWrapper}
        response = self.binding.Send(
            None, None, request, soapaction="http://nbcr.sdsc.edu/opal/getOutputs", **kw
        )
        response = self.binding.Receive(getOutputsResponseWrapper())

        if not isinstance(response, getOutputsResponse) and not issubclass(
            getOutputsResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def launchJob(self, request):
        """
        @param: request to launchJobRequest::
            _launchJobInput: ns1.JobInputType_Def
              _argList: str, optional
              _inputFile: ns1.InputFileType_Def, optional
                _contents: str
                _name: str
              _numProcs: int, optional

        @return: response from launchJobResponse::
            _launchJobOutput: ns1.JobSubOutputType_Def
              _jobID: str
              _status: ns1.StatusOutputType_Def
                _baseURL: str
                _code: int
                _message: str
        """

        if not isinstance(request, launchJobRequest) and not issubclass(
            launchJobRequest, request.__class__
        ):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        response = self.binding.Send(
            None, None, request, soapaction="http://nbcr.sdsc.edu/opal/launchJob", **kw
        )
        response = self.binding.Receive(launchJobResponseWrapper())

        if not isinstance(response, launchJobResponse) and not issubclass(
            launchJobResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def launchJobBlocking(self, request):
        """
        @param: request to launchJobBlockingRequest::
            _launchJobBlockingInput: ns1.JobInputType_Def
              _argList: str, optional
              _inputFile: ns1.InputFileType_Def, optional
                _contents: str
                _name: str
              _numProcs: int, optional

        @return: response from launchJobBlockingResponse::
            _launchJobBlockingOutput: ns1.BlockingOutputType_Def
              _jobOut: ns1.JobOutputType_Def
                _outputFile: ns1.OutputFileType_Def, optional
                  _name: str
                  _url: str
                _stdErr: str, optional
                _stdOut: str, optional
              _status: ns1.StatusOutputType_Def
                _baseURL: str
                _code: int
                _message: str
        """

        if not isinstance(request, launchJobBlockingRequest) and not issubclass(
            launchJobBlockingRequest, request.__class__
        ):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        response = self.binding.Send(
            None,
            None,
            request,
            soapaction="http://nbcr.sdsc.edu/opal/launchJobBlocking",
            **kw
        )
        response = self.binding.Receive(launchJobBlockingResponseWrapper())

        if not isinstance(response, launchJobBlockingResponse) and not issubclass(
            launchJobBlockingResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response

    def queryStatus(self, request):
        """
        @param: request is str

        @return: response from queryStatusResponse::
            _queryStatusOutput: ns1.StatusOutputType_Def
              _baseURL: str
              _code: int
              _message: str
        """

        if not isinstance(request, basestring):
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {"requestclass": queryStatusRequestWrapper}
        response = self.binding.Send(
            None,
            None,
            request,
            soapaction="http://nbcr.sdsc.edu/opal/queryStatus",
            **kw
        )
        response = self.binding.Receive(queryStatusResponseWrapper())

        if not isinstance(response, queryStatusResponse) and not issubclass(
            queryStatusResponse, response.__class__
        ):
            raise TypeError, "%s incorrect response type" % (response.__class__)
        return response


class destroyRequest(ns1.destroyInput_Dec):
    if not hasattr(ns1.destroyInput_Dec(), "typecode"):
        typecode = ns1.destroyInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.destroyInput_Dec.__init__(self, name=None, ns=None)


class destroyRequestWrapper(destroyRequest):
    """wrapper for document:literal message"""

    typecode = destroyRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        destroyRequest.__init__(self, name=None, ns=None)


class destroyResponse(ns1.destroyOutput_Dec):
    if not hasattr(ns1.destroyOutput_Dec(), "typecode"):
        typecode = ns1.destroyOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.destroyOutput_Dec.__init__(self, name=None, ns=None)


class destroyResponseWrapper(destroyResponse):
    """wrapper for document:literal message"""

    typecode = destroyResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        destroyResponse.__init__(self, name=None, ns=None)


class getAppConfigRequest(ns1.getAppConfigInput_Dec):
    if not hasattr(ns1.getAppConfigInput_Dec(), "typecode"):
        typecode = ns1.getAppConfigInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getAppConfigInput_Dec.__init__(self, name=None, ns=None)


class getAppConfigRequestWrapper(getAppConfigRequest):
    """wrapper for document:literal message"""

    typecode = getAppConfigRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getAppConfigRequest.__init__(self, name=None, ns=None)


class getAppConfigResponse(ns1.getAppConfigOutput_Dec):
    if not hasattr(ns1.getAppConfigOutput_Dec(), "typecode"):
        typecode = ns1.getAppConfigOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getAppConfigOutput_Dec.__init__(self, name=None, ns=None)


class getAppConfigResponseWrapper(getAppConfigResponse):
    """wrapper for document:literal message"""

    typecode = getAppConfigResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getAppConfigResponse.__init__(self, name=None, ns=None)


class getAppMetadataRequest(ns1.getAppMetadataInput_Dec):
    if not hasattr(ns1.getAppMetadataInput_Dec(), "typecode"):
        typecode = ns1.getAppMetadataInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getAppMetadataInput_Dec.__init__(self, name=None, ns=None)


class getAppMetadataRequestWrapper(getAppMetadataRequest):
    """wrapper for document:literal message"""

    typecode = getAppMetadataRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getAppMetadataRequest.__init__(self, name=None, ns=None)


class getAppMetadataResponse(ns1.getAppMetadataOutput_Dec):
    if not hasattr(ns1.getAppMetadataOutput_Dec(), "typecode"):
        typecode = ns1.getAppMetadataOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getAppMetadataOutput_Dec.__init__(self, name=None, ns=None)


class getAppMetadataResponseWrapper(getAppMetadataResponse):
    """wrapper for document:literal message"""

    typecode = getAppMetadataResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getAppMetadataResponse.__init__(self, name=None, ns=None)


class getOutputAsBase64ByNameRequest(ns1.getOutputAsBase64ByNameInput_Dec):
    if not hasattr(ns1.getOutputAsBase64ByNameInput_Dec(), "typecode"):
        typecode = ns1.getOutputAsBase64ByNameInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getOutputAsBase64ByNameInput_Dec.__init__(self, name=None, ns=None)


class getOutputAsBase64ByNameRequestWrapper(getOutputAsBase64ByNameRequest):
    """wrapper for document:literal message"""

    typecode = getOutputAsBase64ByNameRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getOutputAsBase64ByNameRequest.__init__(self, name=None, ns=None)


class getOutputAsBase64ByNameResponse(ns1.getOutputAsBase64ByNameOutput_Dec):
    if not hasattr(ns1.getOutputAsBase64ByNameOutput_Dec(), "typecode"):
        typecode = ns1.getOutputAsBase64ByNameOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getOutputAsBase64ByNameOutput_Dec.__init__(self, name=None, ns=None)


class getOutputAsBase64ByNameResponseWrapper(getOutputAsBase64ByNameResponse):
    """wrapper for document:literal message"""

    typecode = getOutputAsBase64ByNameResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getOutputAsBase64ByNameResponse.__init__(self, name=None, ns=None)


class getOutputsRequest(ns1.getOutputsInput_Dec):
    if not hasattr(ns1.getOutputsInput_Dec(), "typecode"):
        typecode = ns1.getOutputsInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getOutputsInput_Dec.__init__(self, name=None, ns=None)


class getOutputsRequestWrapper(getOutputsRequest):
    """wrapper for document:literal message"""

    typecode = getOutputsRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getOutputsRequest.__init__(self, name=None, ns=None)


class getOutputsResponse(ns1.getOutputsOutput_Dec):
    if not hasattr(ns1.getOutputsOutput_Dec(), "typecode"):
        typecode = ns1.getOutputsOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.getOutputsOutput_Dec.__init__(self, name=None, ns=None)


class getOutputsResponseWrapper(getOutputsResponse):
    """wrapper for document:literal message"""

    typecode = getOutputsResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        getOutputsResponse.__init__(self, name=None, ns=None)


class launchJobBlockingRequest(ns1.launchJobBlockingInput_Dec):
    if not hasattr(ns1.launchJobBlockingInput_Dec(), "typecode"):
        typecode = ns1.launchJobBlockingInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.launchJobBlockingInput_Dec.__init__(self, name=None, ns=None)


class launchJobBlockingRequestWrapper(launchJobBlockingRequest):
    """wrapper for document:literal message"""

    typecode = launchJobBlockingRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        launchJobBlockingRequest.__init__(self, name=None, ns=None)


class launchJobBlockingResponse(ns1.launchJobBlockingOutput_Dec):
    if not hasattr(ns1.launchJobBlockingOutput_Dec(), "typecode"):
        typecode = ns1.launchJobBlockingOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.launchJobBlockingOutput_Dec.__init__(self, name=None, ns=None)


class launchJobBlockingResponseWrapper(launchJobBlockingResponse):
    """wrapper for document:literal message"""

    typecode = launchJobBlockingResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        launchJobBlockingResponse.__init__(self, name=None, ns=None)


class launchJobRequest(ns1.launchJobInput_Dec):
    if not hasattr(ns1.launchJobInput_Dec(), "typecode"):
        typecode = ns1.launchJobInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.launchJobInput_Dec.__init__(self, name=None, ns=None)


class launchJobRequestWrapper(launchJobRequest):
    """wrapper for document:literal message"""

    typecode = launchJobRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        launchJobRequest.__init__(self, name=None, ns=None)


class launchJobResponse(ns1.launchJobOutput_Dec):
    if not hasattr(ns1.launchJobOutput_Dec(), "typecode"):
        typecode = ns1.launchJobOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.launchJobOutput_Dec.__init__(self, name=None, ns=None)


class launchJobResponseWrapper(launchJobResponse):
    """wrapper for document:literal message"""

    typecode = launchJobResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        launchJobResponse.__init__(self, name=None, ns=None)


class queryStatusRequest(ns1.queryStatusInput_Dec):
    if not hasattr(ns1.queryStatusInput_Dec(), "typecode"):
        typecode = ns1.queryStatusInput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.queryStatusInput_Dec.__init__(self, name=None, ns=None)


class queryStatusRequestWrapper(queryStatusRequest):
    """wrapper for document:literal message"""

    typecode = queryStatusRequest(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        queryStatusRequest.__init__(self, name=None, ns=None)


class queryStatusResponse(ns1.queryStatusOutput_Dec):
    if not hasattr(ns1.queryStatusOutput_Dec(), "typecode"):
        typecode = ns1.queryStatusOutput_Dec()

    def __init__(self, name=None, ns=None):
        ns1.queryStatusOutput_Dec.__init__(self, name=None, ns=None)


class queryStatusResponseWrapper(queryStatusResponse):
    """wrapper for document:literal message"""

    typecode = queryStatusResponse(name=None, ns=None).typecode

    def __init__(self, name=None, ns=None, **kw):
        queryStatusResponse.__init__(self, name=None, ns=None)
