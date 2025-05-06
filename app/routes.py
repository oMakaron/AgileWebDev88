from app import app

from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from app.model import User, db
from app.forms import SignupForm, LoginForm, UploadForm

from io import BytesIO




@app.route('/logout')
def logout():
    # Logic to log out the user (e.g., clearing session data)
    return redirect('/login')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))

    return render_template("login.html", form=form)

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/edit-profile', methods=['GET', 'PATCH'])
def edit_profile():
    if request.method == 'PATCH':
        # Handle form submission (e.g., save updated profile data)
        name = request.form.get('name')
        email = request.form.get('email')
        # Save the data (this is just a placeholder, implement actual logic)
        print(f"Updated Name: {name}, Updated Email: {email}")
        return redirect('/profile')  # Redirect back to the profile page after saving

    return render_template("edit_profile.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        fullname = form.name.data
        email = form.email.data
        password = form.password.data
        hashed = generate_password_hash(password)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists.")
            return redirect(url_for('login'))
        new_user = User(fullname=fullname, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful!")
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

@app.route('/friends', methods=['GET'])
def friends():
    return render_template('friends.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/add-friend', methods=['GET', 'POST'])
def add_friend():
    return render_template('add_friend.html')


from app.logic.specifier import Parser
from app.logic.plotter import read_csv, save_to_string
from app.plots import registry

from matplotlib.pyplot import close

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    chart = None

    # returns True if the method is POST and the field conforms to all valiadators
    if form.validate_on_submit():

        # parses primitive frame data into useful constructs
        data = read_csv(BytesIO(form.file.data.read()))
        spec = Parser.parse_string(form.spec.data)

        if 'type' not in spec:
            raise Exception('Need a type')

        plot_type = spec.pop('type')
        plot_type = plot_type[0] if isinstance(plot_type, list) else plot_type

        plotter = registry.functions[plot_type]

        # TODO: Catch errors and report the message to the user
        bound, unbound = plotter.bind_args(source = data, **spec)

        if unbound:
            # TODO: Flash these messages to the user so that they can understand why their
            # option isn't doing anything. Maybe make `unbound` also offer near matches?
            print(unbound)

        # generates a base64 encoding of a png so that we don't have to save locally
        figure = plotter.function(**bound)
        image = save_to_string(figure)
        close(figure)

        # this boilerplate is necessary to get the browser to interpret the string as a png
        chart = f"data:image/png;base64,{image}"

    return render_template('upload.html', form=form, chart=chart)


@app.route('/visualise', methods=['GET', 'POST'])
def visualise():
    chart = None
#
# This just needs to be reworked 
#
#    if request.method == 'GET':
#        # Handle visualization logic here
#        x_col = request.args.get('xCol')
#        y_col = request.args.get('yCol')
#        chart_type = request.args.get('chartType')
#        title = request.args.get('title', 'Visualization')
#        color = request.args.get('color', 'blue')
#        grid = request.args.get('grid', '1') == '1'
#        figsize = tuple(map(int, request.args.get('figsize', '10,6').split(',')))
#
#        # Generate the chart using your existing plotting functions
#        if x_col and y_col and chart_type:
#            if chart_type == 'line':
#                chart = plots.plot_line(x_col, y_col, title=title, color=color, grid=grid, figsize=figsize)
#            elif chart_type == 'bar':
#                chart = plots.plot_bar(x_col, y_col, title=title, color=color, grid=grid, figsize=figsize)
#            # Add other chart types here...

    return render_template('visualise.html', chart=chart)

