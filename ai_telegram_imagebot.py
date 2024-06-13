import os
from dotenv import load_dotenv
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import time

class TelegramImageBot:
    def __init__(self, telegram_token, limewire_api_key):
        self.telegram_token = telegram_token
        self.limewire_api_key = limewire_api_key
        self.application = Application.builder().token(telegram_token).build()
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('new', self.new_prompt))
        self.application.add_handler(CommandHandler('change', self.change_prompt))
        self.application.add_handler(CommandHandler('finalize', self.finalize))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.awaiting_prompt = False
        self.prompt = ""

    async def handle_message(self, update: Update, context):
        if self.awaiting_prompt:
            self.prompt = update.message.text
            await update.message.reply_text("Generating image, please wait...")
            image_url = self.generate_image(self.prompt)
            if image_url:
                keyboard = [
                    [InlineKeyboardButton("Is this image correct?", callback_data='correct')],
                    [InlineKeyboardButton("Generate New Image", callback_data='new')],
                    [InlineKeyboardButton("Change Prompt", callback_data='change')],
                    [InlineKeyboardButton("Finalize", callback_data='finalize')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_photo(image_url, caption="Generated Image", reply_markup=reply_markup)
            else:
                await update.message.reply_text("Failed to generate image.")
            self.awaiting_prompt = False
        else:
            await update.message.reply_text("Send me a prompt to generate an image.")
            self.awaiting_prompt = True

    async def start(self, update: Update, context):
        await update.message.reply_text(
            "Welcome to the Image Bot!\n"
            "You can use the following commands:\n"
            "/new - Generate a new image\n"
            "/change - Change the previous prompt\n"
            "/finalize - Finish your session\n"
            "Please send me a prompt to generate an image."
        )
        self.awaiting_prompt = True

    async def new_prompt(self, update: Update, context):
        if update.message:
            await update.message.reply_text("Please send me a new prompt to generate an image.")
        else:
            await update.callback_query.message.reply_text("Please send me a new prompt to generate an image.")
        self.awaiting_prompt = True

    async def change_prompt(self, update: Update, context):
        if update.message:
            await update.message.reply_text(f"Previous prompt: {self.prompt}\nPlease send me the changes to the prompt.")
        else:
            await update.callback_query.message.reply_text(f"Previous prompt: {self.prompt}\nPlease send me the changes to the prompt.")
        self.awaiting_prompt = True

    async def finalize(self, update: Update, context):
        if update.message:
            await update.message.reply_text("Thank you for using the bot. Goodbye!")
        else:
            await update.callback_query.message.reply_text("Thank you for using the bot. Goodbye!")
        self.awaiting_prompt = False

    async def handle_callback(self, update: Update, context):
        query = update.callback_query
        if query.data == 'correct':
            await query.answer("Glad you liked the image!")
        elif query.data == 'new':
            await self.new_prompt(update, context)
        elif query.data == 'change':
            await self.change_prompt(update, context)
        elif query.data == 'finalize':
            await self.finalize(update, context)

    def generate_image(self, prompt):
        url = "https://api.limewire.com/api/image/generation"
        headers = {
            "Authorization": f"Bearer {self.limewire_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            image_url = response.json()["data"][0]["asset_url"]
            return image_url
        else:
            return None

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    LIMEWIRE_API_KEY = os.getenv('LIMEWIRE_API_KEY')
    bot = TelegramImageBot(TELEGRAM_TOKEN, LIMEWIRE_API_KEY)
    bot.run()
