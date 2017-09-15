import json
import re
import uuid
from datetime import datetime
from functools import wraps
from hashlib import md5

from flask import Flask
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from google.cloud import translate as google_translate
from lxml import etree
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .db import Language
from .db import Project
from .db import String
from .db import Suggestion
from .db import Translator
from .db import Vote
from .db import create_scoped_session

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='71a42bbe-9a31-4e4c-b2ee-aa12e5619e1e',
    USERNAME='admin',
    PASSWORD='21232f297a57a5a743894a0e4a801fc3',
))

db = create_scoped_session('sqlite:///db.sqlite')

google_translate_client = google_translate.Client()


@app.teardown_appcontext
def close_db(error):
    db.remove()


@app.cli.command('init-db')
def init_db_command():
    from db import init_database

    init_database(db)

    print('Database initialized.')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('Invalid username', 'warning')
        elif md5(request.form['password']).hexdigest() != app.config['PASSWORD']:
            flash('Invalid password', 'warning')
        else:
            session['logged_in'] = True
            flash('You were logged in')

            return redirect(request.args['next'] if 'next' in request.args else url_for('index'))

    return render_template('login.html')


def requires_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return func(*args, **kwargs)

    return decorated_function


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')

    return redirect(url_for('index'))


@app.route('/')
def index():
    context = {
        'language_count': db.query(Language).count(),
        'project_count': db.query(Project).count(),
    }
    return render_template('index.html', **context)


@app.route('/languages')
def language_list():
    languages = db.query(Language).order_by(Language.name).all()

    return render_template('language_list.html', languages=languages)


@app.route('/languages/new', methods=['GET', 'POST'])
@app.route('/languages/<int:language_id>', methods=['GET', 'POST'])
@requires_login
def language_detail(language_id=None):
    if language_id:
        language = db.query(Language).get(language_id)

        if not language:
            return abort(404)
    else:
        language = Language()

    if request.method == 'POST':
        language.code = request.form['code']
        if language.code:
            language.name = request.form['name']
            if language.name:
                if language.id:
                    db.add(language)
                    db.commit()

                    flash('Language "%s" updated' % language.name)
                else:
                    db.add(language)
                    db.commit()

                    flash('Language "%s" created' % language.name)

                return redirect(url_for('language_list'))
            else:
                flash('Language name is required', 'error')
        else:
            flash('Language code is required', 'error')

    context = {
        'language': language
    }
    return render_template('language_detail.html', **context)


@app.route('/languages/<int:language_id>/delete')
@requires_login
def language_delete(language_id):
    language = db.query(Language).get(language_id)
    if not language:
        return abort(404)

    db.delete(language)
    db.commit()

    flash('Language "%s" deleted' % language.name)

    return redirect(url_for('language_list'))


@app.route('/projects')
def projects():
    all_projects = db.query(Project).order_by(Project.name).all()

    return render_template('projects.html', projects=all_projects)


@app.route('/projects/new', methods=['GET', 'POST'])
@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@requires_login
def project_edit(project_id=None):
    if project_id:
        project = db.query(Project).get(project_id)

        if not project:
            return abort(404)
    else:
        project = Project()
        project.uuid = str(uuid.uuid4())

    if request.method == 'POST':
        project.name = request.form['name'] or None
        if project.name:
            project.language_id = request.form['language_id'] or None
            if project.language_id:
                db.add(project)
                db.commit()

                flash('Project updated' if project_id else 'Project created')

                return redirect(url_for('project_detail', project_id=project.id))
            else:
                flash('Project language is required', 'error')
        else:
            flash('Project name is required', 'error')

    context = {
        'project': project,
        'languages': db.query(Language).order_by(Language.name).all(),
    }
    return render_template('project_edit.html', **context)


@app.route('/projects/<int:project_id>/delete', methods=['GET', 'POST'])
@requires_login
def project_delete(project_id):
    project = db.query(Project).get(project_id)
    db.delete(project)
    db.commit()

    flash('Project "%s" deleted' % project.name)

    return redirect(url_for('projects'))


@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    project = db.query(Project).get(project_id)
    if not project:
        return abort(404)

    context = {
        'project': project,
    }
    return render_template('project.html', **context)


@app.route('/projects/<int:project_id>/strings')
def project_strings(project_id):
    project = db.query(Project).get(project_id)
    if not project:
        return abort(404)

    context = {
        'project': project,
    }
    return render_template('project_strings.html', **context)


@app.route('/projects/<int:project_id>/strings/<int:string_id>')
def project_string(project_id, string_id):
    string = db.query(String).get(string_id)
    if not string or string.project_id != project_id:
        return abort(404)

    context = {
        'string': string,
    }
    return render_template('project_string.html', **context)


@app.route('/projects/<int:project_id>/strings/upload', methods=['POST'])
@requires_login
def project_strings_upload(project_id):
    project = db.query(Project).get(project_id)
    if not project:
        return abort(404)

    if 'file' in request.files and request.files['file']:
        strings_file = request.files['file']

        resources = etree.XML(strings_file.read())
        if resources.tag != 'resources':
            flash('Not a valid strings.xml file', 'error')
        else:
            new_strings = {}
            for resource in resources:
                if resource.tag == 'string' and resource.get('translatable') != 'false':
                    new_strings[resource.get('name')] = dict(
                        action='add',
                        name=resource.get('name'),
                        value=resource.text.strip(),
                        position=resource.sourceline
                    )

            changes = []
            for old_string in project.strings:
                if old_string.name not in new_strings:
                    changes.append(dict(
                        action='remove',
                        name=old_string.name,
                        value=old_string.value,
                        position=old_string.position
                    ))
                else:
                    new_string = new_strings[old_string.name]
                    if new_string['value'] != old_string.value:
                        changes.append(dict(
                            action='merge',
                            name=old_string.name,
                            value=new_string['value'],
                            old_value=old_string.value,
                            position=new_string['position']
                        ))
                    else:
                        changes.append(dict(
                            action='update',
                            name=old_string.name,
                            value=old_string.value,
                            position=new_string['position']
                        ))
                    del new_strings[old_string.name]
            changes.extend(new_strings.values())

            changes.sort(key=lambda item: (item['position'], item['action']))

            context = {
                'project': project,
                'changes': changes,
            }
            return render_template('project_strings_upload.html', **context)

        return redirect(url_for('project_strings', project_id=project_id))

    pattern = re.compile(r'changes\[(\d+)\]\.(.*)')
    changes = {}
    for name, value in request.form.items():
        match = pattern.match(name)
        if match:
            change_index = match.group(1)
            if change_index in changes:
                change = changes[change_index]
            else:
                change = {'index': int(change_index)}
                changes[change_index] = change
            change[match.group(2)] = value

    try:
        for change in changes.values():
            if change['action'] == 'add':
                string = String(project=project, name=change['name'], value=change['value'], position=change['position'])
                db.add(string)
            elif change['action'] == 'merge':
                string = db.query(String).filter(String.project == project, String.name == change['name']).one()
                string.value = change['value']
                string.position = change['position']
                db.merge(string)
                # TODO: apply resolution
            elif change['action'] == 'remove':
                string = db.query(String).filter(String.project == project, String.name == change['name']).one()
                db.delete(string)
            elif change['action'] == 'update':
                string = db.query(String).filter(String.project == project, String.name == change['name']).one()
                string.position = change['position']
                db.merge(string)
        db.commit()

        return redirect(url_for('project_strings', project_id=project_id))
    except Exception:
        db.rollback()

        flash('Something went wrong!')

        changes = changes.values()
        changes.sort(key=lambda item: item['index'])

        context = {
            'project': project,
            'changes': changes,
        }
        return render_template('project_strings_upload.html', **context)


def json_response(response, status=200):
    try:
        json_attr = getattr(response, '__json__')
        if json_attr and callable(json_attr):
            response = response.__json__()
    except AttributeError:
        pass
    response = json.dumps(response, indent=app.debug) + '\n'
    return app.response_class(response, status)


def requires_translator(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            translator_uuid = request.headers.get('X-Translator')
            translator = db.query(Translator).filter(Translator.name == translator_uuid).one()
        except NoResultFound:
            return json_response(dict(error='Translator not found'), 404)

        return func(translator, *args, **kwargs)

    return decorated_function


@app.route('/suggest', methods=['POST'])
@requires_translator
def new_suggestion(translator):
    suggestion_string = db.query(String).get(request.json['string_id'])  # type: String
    if not suggestion_string:
        return json_response(dict(error='String not found'), 404)

    suggestion_language = db.query(Language).get(request.json['language_id'])  # type: Language
    if not suggestion_language:
        return json_response(dict(error='Language not found'), 404)

    suggestion_value = request.json['value']

    existing_suggestions = db.query(Suggestion).filter(
        Suggestion.string == suggestion_string,
        Suggestion.language == suggestion_language,
        Suggestion.value == suggestion_value).all()
    if existing_suggestions:
        suggestion = existing_suggestions[0]

        try:
            db.add(Vote(suggestion=suggestion, translator=translator, value=1))
            db.commit()
        except IntegrityError as error:
            print(error.message)

        return json_response(dict(message='OK'))

    suggestion_google_translation = google_translate_client.translate(
        values=suggestion_value,
        target_language=suggestion_string.project.language.code,
        format_='text',
        source_language=suggestion_language.code,
    )  # type: dict
    suggestion_google_translation = suggestion_google_translation['translatedText']

    suggestion = Suggestion(
        string=suggestion_string,
        translator=translator,
        language=suggestion_language,
        value=suggestion_value,
        google_translation=suggestion_google_translation,
        insert_time=datetime.now()
    )

    try:
        db.add(suggestion)
        db.commit()

        return json_response(suggestion)
    except IntegrityError as error:
        return json_response(dict(error=error.message), 500)


@app.route('/api/v1/projects/<uuid:project_uuid>/languages/<string:language>/status/<uuid:translator_uuid>', methods=['GET'])
def get_translation_status(project_uuid, language, translator_uuid):
    try:
        project = db.query(Project).filter(Project.uuid == str(project_uuid)).one()
    except NoResultFound:
        return json_response(dict(error='Project not found'), 404)

    strings = db.query(String.id).filter(String.project == project).count()

    try:
        language = db.query(Language).filter(Language.code == language).one()
    except NoResultFound:
        try:
            language = db.query(Language).filter(Language.code == language.split('_')[0]).one()
        except NoResultFound:
            return json_response(dict(error='Language not found'), 404)

    if project.language.code == language.code:
        return json_response(dict(error='Language not found'), 404)

    validated = db.execute('''
        select count(1)
            from (
                select distinct string.id
                    from suggestion left join string on suggestion.string_id = string.id
                    where suggestion.accepted = 1 and suggestion.language_id = :language_id and string.project_id = :project_id
            ) as validated
    ''', dict(language_id=language.id, project_id=project.id)).first()[0]

    voted = db.execute('''
        select count(1)
            from (
                select suggestion_id, string_id, votes
                    from ( 
                        select suggestion.id as suggestion_id, suggestion.string_id, sum(vote.value) as votes
                            from suggestion left outer join vote on vote.suggestion_id = suggestion.id left join string on suggestion.string_id = string.id
                            where suggestion.accepted = 1 and suggestion.language_id = :language_id and string.project_id = :project_id
                            group by suggestion.id
                    ) as suggestion_with_votes
                    where votes >= :required_votes
                    group by string_id
            ) as voted
    ''', dict(language_id=language.id, project_id=project.id, required_votes=3)).first()[0]

    return json_response(dict(
        language_code=language.code,
        language_name=language.name,
        strings=strings,
        validated=validated,
        voted=voted,
    ))
