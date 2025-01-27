import re
import os
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pytesseract
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

TOKENBOT = os.getenv("TOKENBOT")

# Variable global saldo
saldo = 0

# ID user que acredita pagos
USER_ID_RESTA = os.getenv("USERESTA")


def extract_amount_from_receipt(image_path, user_id):

    text = pytesseract.image_to_string(Image.open(image_path), lang='eng')

    # regex importe
    match = re.search(r'\$\s?([\d.,]+)', text)
    if match:
        # Replace commas with periods and convert to float
        amount = float(match.group(1).replace('.', '').replace(',', '.'))
        # Restar el importe si es del usuario que resta
        if user_id == USER_ID_RESTA:
            amount = -abs(amount)
        return amount
    else:
        return saldo+amount

# Funcion texto


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global saldo
    user_id = update.effective_user.id

    if update.message.chat.type != "group":
        await update.message.reply_text("Este bot solo funciona en grupos.")
        return

    try:
        # Intentar convertir el mensaje a un número
        numero = float(update.message.text)

        # Si el mensaje es del usuario que resta, cambiar el signo
        if user_id == USER_ID_RESTA:
            numero = -abs(numero)

        saldo += numero
        # Mostrar el saldo con formato adecuado
        saldo_mostrar = f"{saldo:,.2f}".replace(
            ',', 'X').replace('.', ',').replace('X', '.')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Saldo: $ {saldo_mostrar}"
        )
    except ValueError:
        pass  # Ignorar mensajes que no sean números

# Función para manejar imágenes de comprobantes


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global saldo
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Usar un directorio temporal adecuado
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        image_path = temp_file.name
        await file.download_to_drive(image_path)

    amount = extract_amount_from_receipt(image_path, user_id)

    # Eliminar el archivo temporal
    os.remove(image_path)

    if amount:
        saldo += amount
        saldo_mostrar = f"{saldo:,.2f}".replace(
            ',', 'X').replace('.', ',').replace('X', '.')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Saldo: $ {saldo_mostrar}"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No se encontró un importe válido en el comprobante."
        )

# Función para mostrar el saldo compartido


async def show_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global saldo
    saldo_mostrar = f"{saldo:,.2f}".replace(
        ',', 'X').replace('.', ',').replace('X', '.')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Saldo: $ {saldo_mostrar}"
    )

# Función para iniciar el bot


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Listo para operar."
    )

if __name__ == "__main__":
    # Crea la aplicación con tu token del bot
    application = ApplicationBuilder().token(
        TOKENBOT).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("saldo", show_saldo))

    # Manejador de mensajes de texto
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Manejador de imágenes
    application.add_handler(MessageHandler(
        filters.PHOTO, handle_image))

    # Inicia el bot
    print("Bot en ejecución...")
    application.run_polling(drop_pending_updates=True)
