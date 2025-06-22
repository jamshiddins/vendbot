"""Заглушка для auth middleware"""
class AuthMiddleware:
    async def __call__(self, handler, event, data):
        return await handler(event, data)