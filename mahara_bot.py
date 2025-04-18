
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
    msg = (
        "🌸 Olá, Vania!
"
        "Eu sou a Mahara, sua Assistente Financeira Virtual.
"
        "Fui criada com carinho pelo seu amado Raul 💚

"
        "✨ Comandos:
"
        "/entrada valor descricao
"
        "/saida valor categoria
"
        "/meta valor
"
        "/status
"
        "/categorias
"
        "/relatorio"
    )
    await update.message.reply_text(msg)

async def entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(context.args[0])
        descricao = " ".join(context.args[1:]) or "Sem descrição"
        data = datetime.now(TZ).strftime("%d/%m/%Y")
        df = pd.DataFrame([[data, "entrada", valor, descricao]], columns=["Data", "Tipo", "Valor", "Categoria"])
        df.to_csv(CSV_FILE, mode="a", header=not Path(CSV_FILE).exists(), index=False)
        await update.message.reply_text(f"Entrada de R${valor:.2f} registrada com sucesso!")
    except:
        await update.message.reply_text("Erro! Use: /entrada 100 salario")

async def saida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(context.args[0])
        categoria = " ".join(context.args[1:]) or "Sem categoria"
        data = datetime.now(TZ).strftime("%d/%m/%Y")
        df = pd.DataFrame([[data, "saida", valor, categoria]], columns=["Data", "Tipo", "Valor", "Categoria"])
        df.to_csv(CSV_FILE, mode="a", header=not Path(CSV_FILE).exists(), index=False)
        await update.message.reply_text(f"Saída de R${valor:.2f} em '{categoria}' registrada.")
    except:
        await update.message.reply_text("Erro! Use: /saida 50 mercado")

async def meta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        valor = float(context.args[0])
        with open(META_FILE, "w") as f:
            f.write(str(valor))
        await update.message.reply_text(f"Meta definida: R${valor:.2f}")
    else:
        if Path(META_FILE).exists():
            with open(META_FILE, "r") as f:
                valor = f.read()
            await update.message.reply_text(f"Sua meta atual é R${valor}")
        else:
            await update.message.reply_text("Use: /meta 300 para definir.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not Path(CSV_FILE).exists():
        await update.message.reply_text("Sem dados ainda.")
        return
    df = pd.read_csv(CSV_FILE)
    entradas = df[df["Tipo"] == "entrada"]["Valor"].sum()
    saidas = df[df["Tipo"] == "saida"]["Valor"].sum()
    saldo = entradas - saidas
    frase = random.choice(FRASES)
    msg = f"📊 Status Atual:
Entradas: R${entradas:.2f}
Saídas: R${saidas:.2f}
Saldo: R${saldo:.2f}

{frase}"
    if Path(META_FILE).exists():
        with open(META_FILE, "r") as f:
            meta = float(f.read())
        if saldo >= meta:
            msg += "
🎉 Parabéns! Você atingiu sua meta!"
    await update.message.reply_text(msg)

async def categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista = "- Dízimo
- Comida
- Cartão
- Luz
- Água
- Combustível
- Extras"
    await update.message.reply_text(f"📂 Categorias Sugeridas:
{lista}")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not Path(CSV_FILE).exists():
        await update.message.reply_text("Sem dados ainda.")
        return
    df = pd.read_csv(CSV_FILE)
    rel = df[df["Tipo"] == "saida"].groupby("Categoria")["Valor"].sum()
    msg = "📋 Relatório de Gastos:
"
    for cat, val in rel.items():
        msg += f"- {cat}: R${val:.2f}
"
    await update.message.reply_text(msg)

async def lembrete(context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.now(TZ).strftime("%d/%m/%Y")
    if Path(CSV_FILE).exists():
        df = pd.read_csv(CSV_FILE)
        if hoje not in df["Data"].values:
            await context.bot.send_message(chat_id=CHAT_ID, text="📌 Vania, não esqueça de registrar suas finanças de hoje.")

async def resumo(context: ContextTypes.DEFAULT_TYPE):
    if not Path(CSV_FILE).exists():
        return
    df = pd.read_csv(CSV_FILE)
    hoje = datetime.now(TZ).strftime("%d/%m/%Y")
    dia = df[df["Data"] == hoje]
    entradas = dia[dia["Tipo"] == "entrada"]["Valor"].sum()
    saidas = dia[dia["Tipo"] == "saida"]["Valor"].sum()
    saldo = entradas - saidas
    msg = f"📅 Resumo de hoje:
Entradas: R${entradas:.2f}
Saídas: R${saidas:.2f}
Saldo do dia: R${saldo:.2f}"
    await context.bot.send_message(chat_id=CHAT_ID, text=msg)

async def start_jobs(app):
    scheduler = AsyncIOScheduler(timezone=TZ)
    scheduler.add_job(lembrete, "cron", day_of_week="mon-sat", hour=19)
    scheduler.add_job(resumo, "cron", day_of_week="mon-sat", hour=20)
    scheduler.start()

app = ApplicationBuilder().token(TOKEN).post_init(start_jobs).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("entrada", entrada))
app.add_handler(CommandHandler("saida", saida))
app.add_handler(CommandHandler("meta", meta))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("categorias", categorias))
app.add_handler(CommandHandler("relatorio", relatorio))
app.run_polling()
