import flask
import naviance_admissions_calculator
import math
import smtplib
import email

app = flask.Flask(__name__)
app.config.from_pyfile('/etc/naviance_admissions_calculator_web/config.py')
#For encrypting sessions (cookies) when responding to the client
app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

@app.route('/', methods=['GET'])
def get():
    SAT = flask.session.get('SAT')
    GPA = flask.session.get('GPA')
    if SAT:
        SAT = float(SAT)
    if GPA:
        GPA = float(GPA)
    df = naviance_admissions_calculator.all_college_predictions(SAT, GPA)
    df.index = df.index.map(lambda x: x.replace('_', ' '))
    df = df.sort_values(by='chance')
    def report(row):
        if len(row['missing']) == 1:
            return f"Needs {row['missing'][0]}"
        elif len(row['missing']) == 2:
            return "Needs GPA and SAT"
        else: return f'{row["chance"]*100:.0f}'
    for index, row in df.iterrows():
        df.loc[index, 'chance'] = report(row)
    chances_groups = {}
    chances_groups['not_recently_accepted'] = df[df['recently_accepted']==False]
    chances_groups['recently_accepted'] = df[df['recently_accepted']==True]
    def color(string):
        try:
            return float(string)/100*120
        except ValueError:
            return math.nan
    pattern = "^("
    for college in df.index[:-1]:
        pattern += college + "|"
    pattern += college + ")$"
    return flask.render_template('index.html', page='index', chances=df, chances_groups=chances_groups, color=color, pattern=pattern, math=math, len=len, str=str, round=round, float=float)

@app.route('/about', methods=['GET'])
def about():
    return flask.render_template('index.html', page='about')

@app.route('/', methods=['POST'])
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

@app.route('/contact', methods=['POST'])
def contact():
    msg = email.message.EmailMessage()
    msg.set_content(f"From: {flask.request.form.get('email')}\n{flask.request.form.get('text')}")
    msg['Subject'] = 'New contact on LHS Admissions Calculator'
    with open('/etc/naviance_admissions_calculator_web/email_address.txt') as f:
        address = f.read().rstrip()
    msg['From'] = address
    msg['To'] = address
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    return flask.redirect('/')

