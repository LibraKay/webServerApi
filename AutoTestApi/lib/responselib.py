from django.http import JsonResponse
import json


def stderr(code, rawcode, message):
    error = {
        "code": code,
        "rawcode": rawcode,
        "message": message
    }
    return error


def stdJsonResponse(result: bool, data=None, error=None):
    res = {"success": result,
           "data": data,
           "error": error}
    return JsonResponse(res)


def dispatcherBase(request, action2HandlerTable):
    # 将请求参数统一放入request 的 params 属性中，方便后续处理

    # GET请求 参数 在 request 对象的 GET属性中
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST', 'PUT', 'DELETE']:
        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        request.params = json.loads(request.body)

    # 根据不同的action分派给不同的函数进行处理
    action = request.params['action']
    if action in action2HandlerTable:
        handlerFunc = action2HandlerTable[action]
        return handlerFunc(request)

    else:
        error = stderr(1, 0, "action参数错误")
        return stdJsonResponse(False, error=error)
