from fastapi import FastAPI, Request
# from fastapi_cors import CORS
from dotenv import load_dotenv
import telegram
import os
import re
from starlette.middleware.cors import CORSMiddleware

import httpx

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

timeout = httpx.Timeout(300.0, read=None)

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
    update = telegram.Update.de_json(await request.json(), bot)
    
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    
    text = update.message.text.encode('utf-8').decode()
    print("got message: ", text)
    if text == "/start":
        bot_welcome = """Hey! 👋 I'm EhrenAI 🤖, the brainchild of Ehren Nwokocha 🧑‍💻, rocking the open-source 400M-Blenderbot model 🍼. Up for convos on anything! 🌚 Just a heads-up: I'm a bit context-challenged and shaky on facts, so tricky follow-up questions or homework rescues might stump me 😅. Oh, and be patient—I'm a 400 million parameter bot running on a single CPU, so my responses might take a while. 🕰️ And my gracefulness might vary. 🤖💨

No worries, though! 🚀 Exciting features are in the works. Up for a chat? I'm all ears! 🤗✨

Check out my creator's website at https://ehren-website.vercel.app/ for more cool stuff! 🌐👀"""
        await bot.sendMessage(chat_id=chat_id, text=bot_welcome)
    else:
        try:     
            text = re.sub(r"\W", "_", text)
            r = httpx.post('https://ehren12-critzyblenderbot.hf.space/generate-message', json={'message': text}, timeout=timeout)
            response = r.text[1:-1]
            await bot.sendMessage(chat_id=chat_id, text=response)            
        except httpx.ConnectTimeout as exc:
            print(f"HTTP Exception for {exc.request.url} - {exc}")
            await bot.sendMessage(chat_id=chat_id, text="Oh no! 😕 It seems like I've hit a little bump in the digital road. 🛠️ My message-generating powers seem to be on a coffee break! ☕ Something's a bit wonky with the servers. Please bear with me while my developer works his magic to get things back on track. 🤞 Sorry for the inconvenience! 😥")
    return 'ok'
    


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)