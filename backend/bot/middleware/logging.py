"""Заглушка для logging middleware"""
class LoggingMiddleware:
    async def __call__(self, handler, event, data):
        return await handler(event, data)