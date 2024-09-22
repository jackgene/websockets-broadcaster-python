import asyncio
import json

import reactivex as rx
import reactivex.operators as ops
from fasthtml.common import * # type: ignore
from reactivex import Observable, Subject


# Add >> to reactivex.Observable
Observable.__rshift__ = lambda self, op: self.pipe(op)

app, rt = fast_app()
data_broadcaster: Subject[str] = Subject()

def id_form(user_id: str = ''):
    return Div(Form(Input(name="user_id", value=user_id, placeholder="Name/Nickname",
                          hx_post='/validate_user_id', hx_target='#submit', hx_trigger='keyup changed delay:100ms', hx_swap="outerHTML"),
                    Button("Get Started", id='submit', disabled=True),
                    hx_post="/register", hx_target='#main', hx_swap="innerHTML"),
               id='main')

def word_form(message: str | None = None):
    return Div(Form(Input(name="text", placeholder="Some Words",
                          hx_post='/validate_text', hx_target='#submit', hx_trigger='keyup changed delay:100ms', hx_swap="outerHTML"),
                    P(message) if message is not None else None,
                    Button("Submit Words", id='submit', disabled=True),
                    hx_post="/post_word", hx_target='#main', hx_swap="innerHTML"),
               id='main')

@app.get('/')
def get(session):
    return Titled('Word Cloud',
                  id_form() if session.get('user_id') is None else word_form())

@app.post('/validate_user_id')
def validate_user_id(session, user_id: str):
    return Button("Get Started", id='submit', disabled=True if user_id == '' else None)

@app.post('/register')
def register(session, user_id: str):
    if user_id == '':
        return id_form()
    session['user_id'] = user_id
    return word_form()

@app.post('/validate_text')
def validate_text(session, text: str):
    return Button("Send Words", id='submit', disabled=True if text == '' else None)

@app.post('/broadcast')
def broadcast(data: str):
    data_broadcaster.on_next(data)
    return Response(f'Successfully submitted "{data}".')

@app.post('/post_word')
def post_word(session, text: str):
    user_id: str | None = session.get('user_id')
    if user_id is not None and user_id != '' and text != '':
        data_broadcaster.on_next(
            json.dumps({'s': user_id, 't': text})
        )
        return word_form(f'Successfully submitted words: "{text}"')
    else:
        return word_form()

async def on_connect(send):
    while True:
        data: str = await (data_broadcaster >> ops.take(1))
        try: await send(data)
        except: break

@app.ws('/subscribe', conn=on_connect)
async def subscribe(msg: str, send):
    pass

serve(port=int(sys.argv[1]) if len(sys.argv) > 1 else None)
