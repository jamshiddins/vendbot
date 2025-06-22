"""Заглушка для database middleware"""
class DatabaseMiddleware:
    async def __call__(self, handler, event, data):
        return await handler(event, data)