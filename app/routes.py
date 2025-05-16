from functools import wraps
from io import BytesIO, StringIO
import pandas as pd
import json
import os, uuid
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    session, current_app, request
)
from werkzeug.security import check_password_hash
from matplotlib.pyplot import close
from app.extensions import db
from app.models import User, Chart, File
from app.forms import SignupForm, LoginForm, UploadForm, ChartForm
from app.services import read_csv, save_to_string, save_figure_to_file
from app.services import registry

bp = Blueprint('routes', __name__)


# ---------------------------------------------------------------------------------------------------------------------
# Utilities
#

@bp.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'error')
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------------------------------------------------
# Auth routes
#

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('This email is not registered.', 'error')
            return render_template('login.html', form=form)
        if not check_password_hash(user.password, form.password.data):
            flash('Incorrect password.', 'error')
            return render_template('login.html', form=form)

        session['user_id'] = user.id
        flash('Login successful!', 'success')
        return redirect(url_for('routes.dashboard'))
        
    return render_template('login.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('routes.signup'))

        new_user = User(
            fullname=form.name.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful!', 'success')
        return redirect(url_for('routes.login'))
    return render_template('signup.html', form=form)


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('routes.login'))


# ---------------------------------------------------------------------------------------------------------------------
# Main Pages


@bp.route('/')
def index():
    return render_template("index.html")


@bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    charts = Chart.query.filter_by(owner_id=user_id).all()
    return render_template("dashboard.html", charts=charts)


@bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template("profile.html", user=user)


from app.forms import EditProfileForm

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    form = EditProfileForm()

    if form.validate_on_submit():
        user.fullname = form.name.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('routes.profile'))

    form.name.data = user.fullname
    form.email.data = user.email

    return render_template("edit_profile.html", form=form)



@bp.route('/settings')
@login_required
def settings():
    user = db.session.get(User, session['user_id'])
    return render_template('settings.html', user=user)


@bp.route('/friends')
@login_required
def friends():
     return render_template('friends.html')



@bp.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    return render_template('add_friend.html')

@bp.route('/analytics')
@login_required
def analytics():
    return render_template("analytics.html")

# ---------------------------------------------------------------------------------------------------------------------
# Generate Graph Route


@bp.route('/generate-graph', methods=['GET','POST'])
@login_required
def generate_graph():
    upload_form = UploadForm(prefix='up')
    chart_form  = ChartForm(prefix='ch')
    chart       = None
    show_config = False
    data        = None

    # 1) CSV Upload
    if upload_form.submit_upload.data and upload_form.validate_on_submit():
        raw = upload_form.file.data.read()
        df  = read_csv(BytesIO(raw))
        session['csv_string']       = raw.decode('utf-8')
        session['columns']          = df.columns.tolist()
        session['uploaded_filename']= upload_form.file.data.filename

        new_file = File(name=session['uploaded_filename'], owner_id=session['user_id'])
        db.session.add(new_file); db.session.commit()
        session['file_id'] = new_file.id

        return redirect(url_for('routes.generate_graph'))

    # 2) Load DataFrame from session
    if 'csv_string' in session:
        try:
            data = pd.read_csv(StringIO(session['csv_string']))
            cols = session['columns']
            chart_form.x_col.choices  = [('', '– Select X –')]      + [(c,c) for c in cols]
            chart_form.y_col.choices  = [('', '– Select Y –')]      + [(c,c) for c in cols]
            chart_form.column.choices = [('', '– Select column –')] + [(c,c) for c in cols]
            show_config = True
        except Exception as e:
            current_app.logger.error("CSV load failed", exc_info=e)
            flash("Could not reload CSV, please re-upload.", "error")
            session.clear()

    # 3a) Preview
    if data is not None and chart_form.submit_generate.data and chart_form.validate_on_submit():
        # build full spec including DataFrame
        spec = {'source': data}
        for fld in ['title','x_label','y_label','color','grid']:
            v = getattr(chart_form, fld).data
            if v: spec[fld] = v
        if chart_form.figsize.data:
            try:
                w,h = map(int, chart_form.figsize.data.split('x'))
                spec['figsize'] = (w,h)
            except:
                flash("Invalid figure size. Use e.g. 10x6", 'warning')

        t = chart_form.graph_type.data
        spec['graph_type'] = t
        if t in ['line','bar','scatter','area','box']:
            spec['x_col'], spec['y_col'] = chart_form.x_col.data, chart_form.y_col.data
        else:
            spec['column'] = chart_form.column.data

        # draw preview
        bound, _ = registry.functions[t].bind_args(**spec)
        fig       = registry.functions[t].function(**bound)
        raw_b64   = save_to_string(fig)
        close(fig)
        chart     = f"data:image/png;base64,{raw_b64}"

        # store JSON-serializable spec (no DataFrame) for later save
        store_spec = spec.copy()
        store_spec.pop('source', None)
        session['last_spec'] = json.dumps(store_spec)

    # 3b) Save to disk
    elif data is not None and request.method=='POST' and request.form.get('ch-submit_save'):
        # reload spec
        if not session.get('last_spec'):
            flash("Please generate a chart before saving.", "error")
        else:
            store_spec = json.loads(session['last_spec'])
            store_spec['source'] = data

            # draw figure
            bound, _ = registry.functions[store_spec['graph_type']].bind_args(**store_spec)
            fig       = registry.functions[store_spec['graph_type']].function(**bound)

            # persist Chart record
            new_chart = Chart(
                name     = store_spec.get('title','Untitled'),
                owner_id = session['user_id'],
                file_id  = session['file_id'],
                spec     = json.dumps(store_spec)
            )
            db.session.add(new_chart); db.session.commit()

            # save PNG
            fname = save_figure_to_file(fig, new_chart.id)
            close(fig)

            new_chart.image_path = fname
            db.session.commit()

            chart = fname

    return render_template(
        'generate-graph.html',
        upload_form       = upload_form,
        chart_form        = chart_form,
        show_config       = show_config,
        chart             = chart,
        uploaded_filename = session.get('uploaded_filename')
    )

# --------------------------------------------------------------------------------------------------------------------
# Delete Graph Route

@bp.route('/charts/<int:chart_id>/delete', methods=['POST'])
@login_required
def delete_chart(chart_id):
    chart = Chart.query.filter_by(id=chart_id, owner_id=session['user_id']).first()
    if not chart:
        flash("Chart not found or not authorized.", "error")
        return redirect(url_for('routes.dashboard'))

    db.session.delete(chart)
    db.session.commit()
    flash("Chart deleted successfully.", "success")
    return redirect(url_for('routes.dashboard'))
