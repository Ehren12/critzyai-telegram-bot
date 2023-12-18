from fastapi import FastAPI, Request
# from fastapi_cors import CORS
from dotenv import load_dotenv
import telegram
import os
import re
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

global TOKEN
global bot 

TOKEN = os.getenv('BOT_TOKEN')
bot = telegram.Bot(token=TOKEN)

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def index():
    return {"status": "ok"}

@app.get('/setwebhook')
async def set_webhook():
    s = await bot.setWebhook('{URL}{HOOK}'.format(URL=os.getenv('URL'), HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
@app.post('/setwebhook')
async def set_webhook():
    s = await bot.setWebhook('{URL}{HOOK}'.format(URL=os.getenv('URL'), HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.post('/{}'.format(TOKEN))
async def respond(request: Request):
    update = await telegram.Update.de_json(await request.json(), bot)
    
    chat_id = await update.message.chat.id
    msg_id = await update.message.message_id
    
    text = await update.message.text.encode('utf-8').decode()
    print("got message: ", text)
    if text == "/start":
        bot_welcome = """
            Welcome to EhrenAI, your very own Telegram conversational AI developed by Ehren Nwokocha with Meta's Blenderbot400M model.
        """
        
        await bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message=msg_id)
    else:
        try:
            text = re.sub(r"\W", "_", text)
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            await bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message=msg_id)
        except Exception:
            await bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)
    return 'ok'
            


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)