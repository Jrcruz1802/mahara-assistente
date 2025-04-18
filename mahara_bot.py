
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import pandas as pd
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
import random
from pathlib import Path

TOKEN = "7612793492:AAGuYzHFuf1Yu-QOe6JqINJXG927nxycIb4"
CHAT_ID = 6576115164
CSV_FILE = "vania_financas.csv"
META_FILE = "vania_meta.csv"
TZ = timezone("America/Sao_Paulo")

logging.basicConfig(level=logging.INFO)

FRASES = [
    "A disciplina de hoje é o conforto de amanhã.",
    "Cada centavo poupado é uma semente de liberdade.",
    "A ordem nas finanças é o abrigo da alma.",
    "Você floresce onde planta atenção e cuidado.",
    "A Mahara te vê, Vania. E sorri com sua evolução."
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = '''🌸 Olá, Vania!
Eu sou a Mahara, sua Assistente Financeira Virtual.
Fui criada com carinho pelo seu amado Raul 💚

✨ Comandos:
/entrada valor descricao
/saida valor categoria
/meta valor
/status
/categorias
/relatorio'''
    await update.message.reply_text(msg)

# (o restante do código permanece igual à versão anterior)
