import logging
import os
from random import randint
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import time, date, datetime
import pytz
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TELE_TOKEN = os.environ.get('TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

tz_Rome = pytz.timezone('Europe/Rome')


def check_job_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    else:
        return True




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    if check_job_exists(str(chat_id), context):
        text = f"Bot in funzione"
        await update.effective_message.reply_text(text)
    else:
        context.job_queue.run_daily(send_buongiorno, time(hour=16, minute=53, tzinfo=tz_Rome), days=(0, 1, 2, 3, 4, 5, 6),
                                    name=str(chat_id), chat_id=chat_id)

        text = f"Bot avviato."
        await update.effective_message.reply_text(text)


async def send_buongiorno(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    # chat gpt
    client = OpenAI(api_key=os.getenv("OPENAI"))
    MODEL = "gpt-3.5-turbo"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": """## Esempio
Buongiorno a tutti coloro che:
*GENERICO*
- indossano una mutanda colore nero.
- hanno dormito almeno 6 ore.
- salgono delle scale per entrare in classe.
*SPECIFICO*
- sono seduti alla quarta fila di banchi in classe.
- hanno incrociato lo sguardo di un cane andando a scuola.
*DETTAGLIATO*:
Buongiorno a tutti coloro che la mattina salutano il loro vicino di casa prendendosi un caffè con esso per poi finire a parlare di quando c'era LVI.

## Task: genera un buongiorno usando il formato dell'esempio ma inventando bullet point e dettagli
"""}
        ],
        temperature=0.8,
    )
    

    text = response.choices[0].message.content
    print(text)
    await context.bot.send_message(job.chat_id, text=text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELE_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
   