"""
Este programa contiene funciones para gestionar el saldo
de una cuenta corriente en un grupo de telegram.
Incluye operaciones como incrementar, decrementar y consultar el saldo.
Informa el saldo actualizado al grupo cada vez que se realiza una operación.
"""
import re
import os
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import pytesseract
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

TOKENBOT = os.getenv("TOKENBOT")

USER_ID_RESTA = int(os.getenv("USERESTA"))

saldo = 0


def extract_amount_from_receipt(image_path, user_id):
    """ Extraer el importe de un comprobante de pago """
    global saldo
    text = pytesseract.image_to_string(Image.open(image_path), lang='eng')

    # Regex para encontrar importes en formato $ x,xxx.xx o $ x.xxx,xx
    match = re.search(r'\$\s?([\d.,]+)', text)
    if match:
        # Convertir el importe a float
        amount = float(match.group(1).replace('.', '').replace(',', '.'))
        # Restar si es el cliente que abona
        if user_id == USER_ID_RESTA:
            amount = -abs(amount)
        saldo += amount
        return saldo
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Función para manejar importes enviados mensajes de texto """
    global saldo
    user_id = update.effective_user.id

    try:
        # Intentar convertir el mensaje a un número
        numero = float(update.message.text)

        # Restar el número si el mensaje es del usuario que resta
        if user_id == USER_ID_RESTA:
            numero = -abs(numero)

        saldo += numero

        # Mostrar el saldo con formato adecuado
        saldo_mostrar = f"{saldo:,.2f}".replace(
            ',', 'X').replace('.', ',').replace('X', '.')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"$ {saldo_mostrar}"
        )
    except ValueError:
        # Ignorar mensajes que no sean números
        pass


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Función para manejar comprobantes de pago enviados como imágenes """
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
        saldo_mostrar = f"{saldo:,.2f}".replace(
            ',', 'X').replace('.', ',').replace('X', '.')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"$ {saldo_mostrar}"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No se encontró un importe válido en el comprobante."
        )

if __name__ == "__main__":
    # Crea la aplicación con tu token del bot
    application = ApplicationBuilder().token(
        TOKENBOT).build()

    # Manejador de mensajes de texto
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Manejador de imágenes
    application.add_handler(MessageHandler(
        filters.PHOTO, handle_image))

    # Inicia el bot
    print("Bot en ejecución...")
    application.run_polling(drop_pending_updates=True)
