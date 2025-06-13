from dotenv import load_dotenv
import os

load_dotenv()

print(f"BOT_TOKEN from .env: {os.getenv('BOT_TOKEN')}")
print(f"Current directory: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

# Читаем .env напрямую
with open('.env', 'r') as f:
    print("\n.env content:")
    print(f.read())