import json
import sys

import reactivex as rx
import reactivex.operators as ops
from fasthtml.common import * # type: ignore
from reactivex import Observable, Subject


# Add >> to reactivex.Observable
Observable.__rshift__ = lambda self, op: self.pipe(op)

app, rt = fast_app()
broadcaster: Subject[str] = Subject()

def id_form(user_id: str = ''):
    return Div(Form(Input(name='user_id', value=user_id, placeholder='Name/Nickname', autofocus=True,
                          hx_post='/validate_user_id', hx_target='#submit', hx_trigger='keyup changed delay:100ms', hx_swap='outerHTML'),
                    Button('Get Started', id='submit', disabled=True),
                    hx_post='/register', hx_target='#main', hx_swap='innerHTML'),
               id='main')

def word_form(message: str | None = None):
    return Div(Form(Input(name='text', placeholder='Some Words', autofocus=True, autocomplete='off',
                          hx_post='/validate_text', hx_target='#submit', hx_trigger='keyup changed delay:100ms', hx_swap='outerHTML'),
                    P(message) if message is not None else None,
                    Button('Submit Words', id='submit', disabled=True),
                    hx_post='/post_word', hx_target='#main', hx_swap='innerHTML'),
               id='main')

@app.get('/')
def get(session):
    return Titled('Word Cloud',
                  id_form() if session.get('user_id') is None else word_form())

@app.post('/validate_user_id')
def validate_user_id(session, user_id: str):
    return Button('Get Started', id='submit', disabled=True if user_id == '' else None)

@app.post('/register')
def register(session, user_id: str):
    if user_id == '':
        return id_form()
    session['user_id'] = user_id
    return word_form()

@app.post('/validate_text')
def validate_text(session, text: str):
    return Button('Send Words', id='submit', disabled=True if text == '' else None)

@app.post('/broadcast')
def broadcast(text: str):
    broadcaster.on_next(text)
    return Response(f'Successfully submitted "{text}".')

@app.post('/post_word')
def post_word(session, text: str):
    user_id: str | None = session.get('user_id')
    if user_id is not None and user_id != '' and text != '':
        broadcaster.on_next(
            json.dumps({'s': user_id, 't': text})
        )
        return word_form(f'Successfully submitted: "{text}"')
    else:
        return word_form()

async def subscribe_connected(send):
    keep_alives: Observable[None] = rx.interval(300) >> ops.map(lambda _: '')
    messages: Observable[str] = broadcaster >> ops.merge(keep_alives)
    while True:
        message: str = await (messages >> ops.take(1))
        try: await send(message)
        except: break

@app.ws('/subscribe', conn=subscribe_connected)
async def subscribe():
    pass

serve(port=int(sys.argv[1]) if len(sys.argv) > 1 else None)
