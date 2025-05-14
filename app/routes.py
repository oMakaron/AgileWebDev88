from functools import wraps
from io import BytesIO, StringIO
import pandas as pd
import json

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    session, current_app, jsonify
)
from werkzeug.security import check_password_hash
from matplotlib.pyplot import close

from app.extensions import db
from app.models import User, Chart
from app.forms import SignupForm, LoginForm, UploadForm, ChartForm
from app.services import Parser, registry, read_csv, save_to_string


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


@bp.route('/generate-graph', methods=['GET', 'POST'])
@login_required
def generate_graph():
    upload_form = UploadForm(prefix='up')
    chart_form  = ChartForm(prefix='ch')
    chart       = None
    show_config = False
    data        = None

    # --- 1. Handle File Upload ---
    if upload_form.submit_upload.data and upload_form.validate_on_submit():
        file_data = upload_form.file.data.read()
        df = read_csv(BytesIO(file_data))

        session['csv_string']     = file_data.decode('utf-8')
        session['columns']        = df.columns.tolist()
        session['uploaded_filename'] = upload_form.file.data.filename

        from app.models import File
        new_file = File(name=session['uploaded_filename'], owner_id=session['user_id'])
        db.session.add(new_file)
        db.session.commit()
        session['file_id'] = new_file.id

        return redirect(url_for('routes.generate_graph'))

    # --- 2. Load DataFrame from session ---
    if 'csv_string' in session:
        try:
            data = pd.read_csv(StringIO(session['csv_string']))
            cols = session['columns']
            chart_form.x_col.choices = [('', '– Select X –')] + [(c, c) for c in cols]
            chart_form.y_col.choices = [('', '– Select Y –')] + [(c, c) for c in cols]
            chart_form.column.choices = [('', '– Select column –')] + [(c, c) for c in cols]
            show_config = True
        except Exception as e:
            flash("Failed to load saved CSV data. Try re-uploading.", "error")
            current_app.logger.error("CSV read error", exc_info=e)
            session.clear()

    # --- 3. Chart Generation ---
    if chart_form.submit_generate.data and chart_form.validate_on_submit() and data is not None:
        try:
            plot_type = chart_form.graph_type.data
            plotter   = registry.functions.get(plot_type)

            # build args from form
            args = {'source': data}
            for attr in ['title','x_label','y_label','color','figsize']:
                val = getattr(chart_form, attr).data
                if val:
                    args[attr] = val

            if chart_form.grid.data:
                args['grid'] = chart_form.grid.data

            if chart_form.figsize.data:
                try:
                    w,h = map(int, chart_form.figsize.data.split('x'))
                    args['figsize'] = (w,h)
                except ValueError:
                    flash("Invalid figure size. Use e.g. 10x6", 'warning')

            # column selections
            if plot_type in ['line','bar','scatter','area','box']:
                args['x_col'] = chart_form.x_col.data
                args['y_col'] = chart_form.y_col.data
            elif plot_type == 'histogram':
                args['column'] = chart_form.column.data
                for attr in ['bins','density','cumulative','orientation','histtype','alpha']:
                    val = getattr(chart_form, attr).data
                    if val:
                        args[attr] = val
            elif plot_type == 'pie':
                args['column'] = chart_form.column.data
                for attr in ['angle','explode','autopct','shadow','radius','pctdistance','labeldistance','colors']:
                    val = getattr(chart_form, attr).data
                    if val:
                        args[attr] = val

            # Generate the figure
            bound, _ = plotter.bind_args(**args)
            fig       = plotter.function(**bound)

            # Capture raw base64 (no prefix) for preview + storage
            raw_b64 = save_to_string(fig)
            chart   = f"data:image/png;base64,{raw_b64}"
            close(fig)

            # Clean up for DB
            args.pop('source', None)
            args['graph_type'] = plot_type

            # Save Chart with image_data
            from app.models import Chart
            new_chart = Chart(
                name       = args.get('title') or 'Untitled',
                owner_id   = session['user_id'],
                file_id    = session.get('file_id'),
                spec       = json.dumps(args),
                image_data = raw_b64
            )
            db.session.add(new_chart)
            db.session.commit()

        except Exception as e:
            current_app.logger.error("Chart generation failed", exc_info=e)
            flash(f"Chart error: {e}", "error")

    return render_template(
        "generate-graph.html",
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
