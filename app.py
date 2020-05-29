from flask import Flask, render_template

app = Flask(__name__,
            template_folder='template')

app.config['ENV'] = 'Development'
app.config['DEBUG'] = True

@app.route('/')
def index():
    pass
    return render_template('template.html',
                            message="안녕하세요?")



app.run(port='5000')