import json

from aiohttp import web
from aiohttp.web import middleware, Request, Response
from datetime import datetime, timedelta
from jwt import decode, DecodeError, encode, ExpiredSignatureError
from typing import Callable, List
from yarl import URL


def json_response(dict_: dict) -> Response:
    """
    Возвращает Response в виде json для заданного словаря
    :param dict_: словарь
    :type dict_: dict
    :return: Response
    :rtype: Response
    """
    return Response(text=json.dumps(dict_, ensure_ascii=False))


def get_token(payload: dict, expiration_s=3600, algorithm='HS256', secret='') -> str:
    """
    Возвращает jwt-токен для заданного словаря
    :param payload: словарь
    :type payload: dict
    :param expiration_s: время действия токена, с
    :type expiration_s: int
    :param algorithm: алгоритм формирования токена
    :type algorithm: str
    :param secret: секрет
    :type secret: str
    :return: jwt-токен
    :rtype: str
    """
    payload['exp'] = datetime.utcnow() + timedelta(seconds=expiration_s)
    return encode(payload, secret, algorithm)


def middleware_factory(whitelist=None, secret='', algorithm='HS256',
                       auth_scheme='Bearer') -> List[Callable]:
    """
    Формирует middleware для aiohttp
    :param whitelist: список публичных URL (не требуют авторизационного токена)
    :type whitelist: List[str]
    :param secret: секрет
    :type secret: str
    :param algorithm: алгоритм формирования токена
    :type algorithm: str
    :param auth_scheme: схема аутентификации
    :type auth_scheme: str
    :return: список middleware для передачи в aiohttp.web.Application
    :rtype: List[Callable]
    """
    if whitelist is None:
        whitelist = []

    if secret == '':
        raise web.HTTPServerError(reason='Missing jwt secret')

    @middleware
    async def _auth_middleware(request: Request, handler) -> Response:
        if request.rel_url.path in whitelist:
            return await handler(request)

        try:
            jwt_token = request.headers.get('Authorization')
            if jwt_token and jwt_token.startswith(auth_scheme):
                jwt_token = jwt_token[len(auth_scheme) + 1:].strip()
            else:
                raise KeyError

            # приклеиваем ко всем запросам параметры из расшифрованного токена
            payload = decode(jwt_token, secret, algorithms=[algorithm])
            query = dict(request.rel_url.query)
            request = request.clone(rel_url=URL.build(query=(query | payload)))

            response = await handler(request)
        except KeyError:
            raise web.HTTPUnauthorized(reason='Missing authorization token')
        except DecodeError:
            raise web.HTTPUnauthorized(reason='Incorrect authorization token')
        except ExpiredSignatureError:
            raise web.HTTPForbidden(reason='Authorization token is expired')

        return response

    return [_auth_middleware]
