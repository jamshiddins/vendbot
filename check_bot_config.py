#!/usr/bin/env python3
"""
Скрипт для проверки информации о текущем боте
"""

import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

async def check_bot_info():
    """Проверяет информацию о боте по токену"""
    
    try:
        from aiogram import Bot
        from aiogram.types import BotCommand
        
        # Получаем токен из переменных окружения
        bot_token = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not bot_token or bot_token in ['YOUR_BOT_TOKEN_HERE', 'YOUR_REAL_BOT_TOKEN_HERE']:
            print("❌ Токен бота не настроен!")
            print("🔧 Пожалуйста, настройте BOT_TOKEN в файле .env")
            return
        
        print("🔍 Проверка информации о боте...")
        print("=" * 50)
        
        # Создаем экземпляр бота
        bot = Bot(token=bot_token)
        
        try:
            # Получаем информацию о боте
            me = await bot.get_me()
            
            print(f"✅ Подключение успешно!")
            print(f"🤖 Имя бота: {me.first_name}")
            print(f"📝 Username: @{me.username}")
            print(f"🆔 ID бота: {me.id}")
            print(f"📱 Токен: {bot_token[:10]}...{bot_token[-4:]}")
            
            # Проверяем может ли бот отправлять сообщения
            if me.can_join_groups:
                print("✅ Может присоединяться к группам")
            if me.can_read_all_group_messages:
                print("✅ Может читать все сообщения в группах")
            if me.supports_inline_queries:
                print("✅ Поддерживает inline запросы")
            
            # Получаем список команд бота
            try:
                commands = await bot.get_my_commands()
                if commands:
                    print(f"\n📋 Команды бота ({len(commands)}):")
                    for cmd in commands:
                        print(f"   /{cmd.command} - {cmd.description}")
                else:
                    print("\n📋 Команды не настроены")
            except Exception as e:
                print(f"\n⚠️ Не удалось получить команды: {e}")
            
            print("\n" + "=" * 50)
            print("✅ Это правильный бот для VendBot?")
            print("❓ Если НЕТ, то:")
            print("1. Получите правильный токен у @BotFather")
            print("2. Замените BOT_TOKEN в файле .env")
            print("3. Перезапустите проверку")
            
        except Exception as e:
            print(f"❌ Ошибка при подключении к боту: {e}")
            print("🔧 Возможные причины:")
            print("   • Неверный токен")
            print("   • Бот заблокирован")
            print("   • Проблемы с интернетом")
            
        finally:
            await bot.session.close()
            
    except ImportError:
        print("❌ Библиотека aiogram не установлена!")
        print("🔧 Установите: pip install aiogram")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

def show_bot_setup_guide():
    """Показывает руководство по настройке бота"""
    
    print("\n📚 РУКОВОДСТВО ПО НАСТРОЙКЕ БОТА")
    print("=" * 50)
    
    print("\n🆕 Создание нового бота:")
    print("1. Откройте Telegram")
    print("2. Найдите @BotFather")
    print("3. Отправьте /newbot")
    print("4. Введите название: VendBot")
    print("5. Введите username: ваш_уникальный_vendbot")
    print("6. Скопируйте токен (формат: 1234567890:XXXXXXXXX)")
    
    print("\n🔧 Настройка существующего бота:")
    print("1. Найдите @BotFather")
    print("2. Отправьте /mybots")
    print("3. Выберите нужного бота")
    print("4. Выберите 'API Token'")
    print("5. Скопируйте токен")
    
    print("\n⚙️ Настройка в проекте:")
    print("1. Откройте файл .env")
    print("2. Найдите строку: BOT_TOKEN=YOUR_BOT_TOKEN_HERE")
    print("3. Замените на: BOT_TOKEN=ваш_реальный_токен")
    print("4. Сохраните файл")
    print("5. Перезапустите: python main.py")
    
    print("\n✅ Проверка:")
    print("1. Запустите: python check_bot_info.py")
    print("2. Найдите вашего бота в Telegram")
    print("3. Отправьте /start")

if __name__ == "__main__":
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("🔧 Создайте .env файл с настройками")
        show_bot_setup_guide()
    else:
        # Запускаем проверку
        asyncio.run(check_bot_info())
        show_bot_setup_guide()