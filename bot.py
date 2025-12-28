import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types # Importante para as ferramentas
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- FERRAMENTAS DO AGENTE (TOOLS) ---

def listar_arquivos_projeto():
    """Lista todos os arquivos presentes na pasta atual do projeto."""
    try:
        arquivos = os.listdir('.')
        return f"Arquivos na pasta: {', '.join(arquivos)}"
    except Exception as e:
        return f"Erro ao acessar arquivos: {e}"

# --- CONFIGURAÇÃO DO CLIENTE ---

client = genai.Client(api_key=GEMINI_KEY)
config_agente = {
    "tools": [listar_arquivos_projeto]
}

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    status_msg = await update.message.reply_text("Consultando sistema...")

    try:
        # O parâmetro 'config' permite que o Gemini use a função listar_arquivos_projeto
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=user_text,
            config=types.GenerateContentConfig(
                tools=[listar_arquivos_projeto]
            )
        )
        
        # O Gemini processa a ferramenta e gera o texto final
        answer = response.text
        await status_msg.edit_text(answer) # pyright: ignore[reportArgumentType]

    except Exception as e:
        print(f"Erro: {e}")
        await status_msg.edit_text("Ops, tive um problema técnico. Tente novamente!")

def main():
    print("Agente Antigravity com acesso a arquivos iniciado!")
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = Application.builder().token(TELEGRAM_TOKEN).request(request).build() # pyright: ignore[reportArgumentType]
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()

if __name__ == "__main__":
    main()