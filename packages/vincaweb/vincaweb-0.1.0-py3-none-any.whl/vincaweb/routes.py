import sqlite3
from flask import render_template, request, redirect, session
from vincaweb import vincaweb as app
app.config.from_mapping(SECRET_KEY='dev',)
import time
from contextlib import contextmanager
today = time.time() / 86400

from vinca._card import Card
from vinca._cardlist import Cardlist

def days_rounder(n):
    'express number of days as weeks, months, years, etc.'
    a = abs(n)
    if a <= 9:
        return str(n)+'d'
    elif a <= 69:
        return str(n//7)+'w'
    elif a <= 299:
        return str(n//30)+'m'
    elif a <= 3599:
        return str(n//360)+'y'
    else:
        return str(n/3600)+'X'


# @contextmanager
def get_db_cursor():
    return sqlite3.connect('tutorial_cards.db').cursor()
    # conn = sqlite3.connect('tutorial_cards.db')
    # yield conn.cursor()
    # conn.commit()
    # conn.close()
def get_card(id):
    return Card(id, sqlite3.connect('tutorial_cards.db').cursor())
def get_cardlist():
    cardlist = Cardlist(sqlite3.connect('tutorial_cards.db').cursor())
    filter_params = {key: session[key] for key in default_filter_params}
    cardlist = cardlist.filter(**filter_params)
    cardlist = cardlist.sort(session['sort_by'])
    if session['search']:
        cardlist = cardlist.findall(session['search'])
    return cardlist
    # TODO we set all the filter criteria of the cardlist based on the session filter criteria

@app.route('/set_session_param/<option>/<value>',methods=['GET','POST'])
@app.route('/set_session_param/<option>/',methods=['GET','POST'])
def set_session_param(option, value=None):
    log(option, value)
    casting = {'True':True, 'False':False, 'None':None}
    value = casting.get(value, value)
    session[option] = value
    return redirect('/home')

default_misc_params = {
   'initialized': False,
   'sort_by': 'seen',
   'search': None,
   'advanced_filters_visible': False,
}
default_filter_params = {
   'require_parameters': False,
   'created_after': None,
   'created_before': None,
   'due_after': None,
   'due_before': None,
   'deleted': None,
   'due': None,
   'new': None,
   'contains_images': None,
   'card_type': None,
   'tag': None,
   'invert': False,
}
default_session = dict(**default_misc_params, **default_filter_params)

def log(*args):
    print(*args,file=open('/home/oscar/log','w'))

@app.before_request
def init_session():
    if not session.get('initialized'):
        session.update(default_session)
        session['initialized'] = True

@app.route('/home') 
def home():
    matching_cards = get_cardlist().explicit_cards_list(LIMIT = 80)
    # with get_db_cursor() as c:
        # c.execute('SELECT id, front_text, deleted FROM cards WHERE 1')
        # matching_cards = c.fetchall()
    basic_action_links = render_template('basic_action_links.tpl', cards = matching_cards, **session)
    return basic_action_links

@app.route('/create/<card_type>')
def create(card_type):
    # TODO I could allow creation during review with a callback to review all
    assert card_type in ('basic','verses')
    card = Card._new_card(get_db_cursor())
    card.card_type = card_type
    return redirect(f'/edit/{card.id}')

@app.route('/review/<id>')
def review(id):
    card = get_card(id)
    session['review_start_time'] = time.time()
    if card.card_type == 'basic':
        return render_template('review_basic.tpl', card=card)
    elif card.card_type == 'verses':
        return render_template('review_verses.tpl', card=card)

@app.route('/preview/<id>')
def preview(id):
    card = get_card(id)
    if card.card_type == 'basic':
        return render_template('preview_basic.tpl', card=card)
    elif card.card_type == 'verses':
        return render_template('preview_verses.tpl', card=card)

@app.route('/grade/<grade>/<card_id>')
def grade(grade, card_id):
    if 'review_start_time' in session:
        review_end_time = time.time()
        elapsed_seconds = review_end_time - review_start_time
        elapsed_seconds = min(elapsed_seconds, 60)
    else:
        elapsed_seconds = 0
    card = get_card(card_id)
    card._log(grade, elapsed_seconds)
    return redirect('/review_all')


@app.route('/review_all')
def review_all():
    # dispatches the reviews
    # finds the next due card to study
    # after the card is graded we are redirected back here
    # to be given another due card
    cardlist = get_cardlist().filter(due = True, deleted = False)
    if cardlist:
        # !! I use a nonstandard indexing for cardlists which starts at 1 !!
        # (This makes the cli more intuitive, but is more confusing in the code)
        next_card = cardlist[1] 
        return redirect(f'/review/{next_card.id}')
    else:
        return redirect('/home')

@app.route('/edit/<callback>/<id>', methods=['GET','POST'])
@app.route('/edit/<id>', methods=['GET','POST'])
def edit(id, callback=None):
    card = get_card(id)

    if request.form.get('save', False):
        for field in ('front_text','back_text'):
            card[field] = request.form[field]
        if callback:
            return redirect(f'/review/{card.id}')
        else:
            return redirect('/home')
    else:
        return render_template('edit.tpl', front_text=card.front_text, front_image=card.front_image,
                  back_text=card.back_text, back_image=card.back_image, id=card.id)

@app.route('/delete/<id>', methods=['GET','POST'])
@app.route('/delete/<id>/<callback>')
def delete(id, callback=False):
    # add constraint isdue
    # with get_db_cursor() as c:
        # c.execute('UPDATE cards SET deleted = not deleted WHERE id = ?',(id,))
    card = get_card(id)
    card.deleted = not card.deleted
    if callback: #go back to review
        return redirect('/review_all')
    else:
        return redirect('/home')

@app.route('/statistics')
def statistics():
    return 'you have several cards'

@app.route('/purge')
def purge():
    cardlist = get_cardlist()
    cardlist.purge(confirm = False)
    return redirect('/home')
