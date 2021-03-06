import flask
import naviance_admissions_calculator
import math
import smtplib
import email
import json
import pickle
import franca_link.my_logging as my_logging

wrapper_related = my_logging.wrapper_related('franca_link.calculator')
wrapper = wrapper_related.wrapper

app = flask.Blueprint('calculator', __name__, template_folder='templates', static_folder='static')

_get = wrapper()
@app.route('/', methods=['GET'])
@_get
def get():
    colleges = naviance_admissions_calculator.get_college_names()
    colleges = [x.replace('_',' ') for x in colleges]
    pattern = "^("
    for college in colleges[:-1]:
        pattern += college + "|"
    pattern += colleges[-1] + ")$"
    return flask.render_template('naviance_admissions_calculator_web/index.html', pattern=pattern)

_api = wrapper()
@app.route('/api', methods=['GET'])
@_api
def api():
    #Test
    def present(obj):
        return not obj == None and not obj == 'undefined' and not obj == ''
    SAT = flask.request.cookies.get('stand')
    if present(SAT):#this might be the source of 0s being ignored
        if flask.request.cookies.get('radio') == 'act':
            SAT = naviance_admissions_calculator.act_to_sat(SAT)
        else: SAT = float(SAT)
    else: SAT = None
    GPA = flask.request.cookies.get('gpa')
    if present(GPA):
        GPA = float(GPA)
    else: GPA = None
    df = naviance_admissions_calculator.all_college_predictions(SAT, GPA)
    df.index = df.index.map(lambda x: x.replace('_', ' '))
    df.insert(0, 'rank', None)
    with open('rankings.pickle', 'rb') as f:
        rankings = pickle.load(f)
    for index, row in df.iterrows():
        df.loc[index, 'rank'] = rankings.get(index)
    df = df.sort_values(['rank','chance'])
    def color(value):
        try:
            return value*120
        except ValueError:
            return math.nan
    for index, row in df.iterrows():
        if len(row['missing']) > 0: df.loc[index, 'color'] = None
        else: df.loc[index, 'color'] = color(row['chance'])
    def report(row):
        if len(row['missing']) == 1:
            if row['missing'][0] == 'SAT':
                return f"Needs SAT or ACT"
            return f"Needs GPA"
        elif len(row['missing']) == 2:
            return "Needs GPA and SAT or ACT"
        else: return f'{row["chance"]*100:.0f}%'
    for index, row in df.iterrows():
        df.loc[index, 'chance'] = report(row)
    #Turns index into a column
    df.reset_index(inplace=True)
    #table = [{'name': 'SAT', 'chance':SAT, 'color':0},
    #        {'name':'GPA', 'chance':GPA, 'color': None}]
    return df.to_json(orient='records')

_about = wrapper()
@app.route('/about', methods=['GET'])
@_about
def about():
    return flask.render_template('naviance_admissions_calculator_web/about.html')

_post = wrapper()
@app.route('/', methods=['POST'])
@_post
def post():
    for name, value in flask.request.form.items():
        flask.session[name] = value
        #print(name)
        #print(type(value))
        #print(value)
    #goto = '/'
    #if flask.session.get('GPA') or flask.session.get('SAT'):
    #    print(flask.session.get('GPA'))
    #    print(flask.session.get('SAT'))
#        goto += '#search_area'
    return flask.redirect('/')

def contact():
    request = flask.request.json
    print(request)
    msg = email.message.EmailMessage()
    msg.set_content(f"From: {request.get('email')}\n{request.get('text')}")
    msg['Subject'] = 'New contact on LHS Admissions Calculator'
    with open('/etc/naviance_admissions_calculator_web/email_address.txt') as f:
        msg['From'] = f.readline().rstrip()
        msg['To'] = f.readline().rstrip()
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    return flask.jsonify(success=True)

