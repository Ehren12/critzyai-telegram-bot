from fastapi import FastAPI, Request
from dotenv import load_dotenv
import telegram
import os
import re

load_dotenv()

global TOKEN
global bot 

TOKEN = os.getenv('BOT_TOKEN')
bot = telegram.Bot(token=TOKEN)

app = FastAPI()

@app.post('/{}'.format(TOKEN))
def respond(request: Request):
    update = telegram.Update.de_json(request.json(), bot)
    
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    
    text = update.message.text.encode('utf-8').decode()
    print("got message: ", text)
    if text == "/start":
        bot_welcome = """
            Welcome to EhrenAI, your very own Telegram conversational AI developed by Ehren Nwokocha with Meta's Blenderbot400M model.
        """
        
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message=msg_id)
    else:
        try:
            text = re.sub(r"\W", "_", text)
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message=msg_id)
        except Exception:
            bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
            
@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)