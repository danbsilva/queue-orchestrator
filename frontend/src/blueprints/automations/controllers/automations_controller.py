import json
from flask import render_template, request, redirect, url_for, session, flash
from src.blueprints.automations.forms.automations_forms import AutomationForm
from src.blueprints.automations.forms.steps_forms import StepForm
from src.blueprints.automations.forms.items_forms import ItemForm, create_dynamic_fields
from src.blueprints.automations.forms.fields_forms import FieldForm
from src.blueprints.automations.forms.owners_forms import OwnerForm


from src.repositories import automations_repository, users_repository
from src.blueprints.auth.security import login_required
from src.helpers import convert_error_to_tuple


def return_automation(automation_uuid):
    automation = {}
    response, code = automations_repository.automation(uuid=automation_uuid)
    if code == 200:
        automation = response['automation']

    return automation


def return_steps(automation):
    steps = []
    try:
        response, code = automations_repository.steps(automation_uuid=automation['uuid'], page=1, per_page=100)
        if code == 200:
            steps = response['steps']
    except Exception as e: ...

    return steps


def return_fields(step):
    fields = []
    try:
        response, code = automations_repository.fields(step_uuid=step['uuid'], page=1, per_page=100)
        if code == 200:
            fields = response['fields']
    except Exception as e: ...

    return fields


### AUTOMATIONS ###
@login_required.verify_login
def automations():
    return render_template('automations/automations.html')


@login_required.verify_login
def page_automations():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)

    if session['is_admin']:
        response, code = automations_repository.automations(page=page, per_page=per_page, search=search)
    else:
        response, code = automations_repository.my_automations(page=page, per_page=per_page, search=search)
    if code == 200:
        automations = response['automations']
        pagination = response['pagination']
        return render_template('automations/automations-list.html', automations=automations, pagination=pagination)

    return render_template('automations/automations-list.html', automations=[])


@login_required.verify_login
def new_automation():
    errors = []
    form = AutomationForm(request.form)
    if request.method == 'POST':
        args = form.data
        if form.validate_on_submit():

            args.pop('csrf_token')
            args.pop('submit')
            args.pop('uuid')

            response, code = automations_repository.new_automation(data=args)
            if code == 201:
                return response['automation'], code
            errors = convert_error_to_tuple(response)
            return errors, code
        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    return render_template('automations/automation-new.html', form=form)


@login_required.verify_login
def edit_automation(uuid):
    errors = []
    form = AutomationForm(request.form)
    if request.method == 'POST':
        args = form.data
        if form.validate_on_submit():

            args.pop('csrf_token')
            args.pop('submit')
            args.pop('uuid')

            response, code = automations_repository.edit_automation(uuid=uuid, data=args)
            if code == 200:
                return response['automation'], code
            errors = convert_error_to_tuple(response)
            return errors, code
        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    response, code = automations_repository.automation(uuid=uuid)
    if code == 200:
        automation = response['automation']
        form = AutomationForm(**automation)
        return render_template('automations/automation-edit.html', form=form)

    return response['message'], code


@login_required.verify_login
def view_automation(uuid):
    automation = return_automation(uuid)
    steps = return_steps(automation)
    return render_template('automations/automation-view.html', automation=automation, steps=steps)


@login_required.verify_login
def detail_automation(uuid):
    response, code = automations_repository.automation(uuid=uuid)
    if code == 200:
        automation = response['automation']
        return render_template('automations/automation-detail.html', automation=automation)

    return response['message'], code


@login_required.verify_login
def delete_automation(uuid):
    response, code = automations_repository.delete_automation(uuid=uuid)
    return response['message'], code


#### OWNERS ####
@login_required.verify_login
def page_owners(automation_uuid):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)

    response, code = automations_repository.automation(uuid=automation_uuid)
    if code == 200:
        automation = response['automation']

    response, code = automations_repository.owners(automation_uuid=automation_uuid, page=page, per_page=per_page, search=search)
    if code == 200:
        owners = response['owners']
        pagination = response['pagination']
        return render_template('automations/owners-list.html', owners=owners, pagination=pagination, automation=automation)

    return response['message'], code


@login_required.verify_login
def new_owner(automation_uuid):
    errors = []
    automation = {}
    users = []

    form = OwnerForm(request.form)
    form.owner.choices = []
    if request.method == 'POST':
        args = form.data
        args.pop('csrf_token')
        args.pop('submit')

        if not args['owner']:
            return [['owner', ['O proprietário é obrigatório']]], 400

        owner = {'uuid': args['owner']}
        response, code = automations_repository.new_owner(automation_uuid=automation_uuid, data=owner)
        if code == 201:
            return 'Proprietário criado com sucesso', code

        errors = convert_error_to_tuple(response)
        return errors, code
    else:
        response, code = users_repository.users()
        if code == 200:
            users = response['users']

        response, code = automations_repository.automation(uuid=automation_uuid)
        if code == 200:
            automation = response['automation']
            return render_template('automations/owner-new.html', form=form, automation=automation, users=users)

    return response['message'], code


@login_required.verify_login
def delete_owners(automation_uuid):
    uuid = request.args.get('uuid', '', type=str)

    owner = {'uuid': uuid}
    response, code = automations_repository.delete_owners(automation_uuid=automation_uuid, data=owner)
    if code == 200:
        return 'Proprietário excluído com sucesso', code
    else:
        return 'Erro ao excluir proprietário', code


#### STEPS ####
@login_required.verify_login
def steps():
    return render_template('steps/steps.html')


@login_required.verify_login
def page_steps(automation_uuid):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    per_page = request.args.get('per_page', 10, type=int)

    response, code = automations_repository.steps(automation_uuid=automation_uuid, page=page, per_page=per_page, search=search)
    if code == 200:
        steps = response['steps']
        pagination = response['pagination']

        response, code = automations_repository.automation(uuid=automation_uuid)
        if code == 200:
            automation = response['automation']
            return render_template('steps/steps-list.html', steps=steps, pagination=pagination, automation=automation)

    return response['message'], code


@login_required.verify_login
def new_step(automation_uuid):
    errors = []
    automation = {}
    form = StepForm(request.form)

    if request.method == 'POST':
        args = form.data
        if form.validate_on_submit():

            args.pop('csrf_token')
            args.pop('submit')
            args.pop('uuid')

            response, code = automations_repository.new_step(automation_uuid=automation_uuid, data=args)
            if code == 201:
                return 'Etapa criada com sucesso', code

            errors = convert_error_to_tuple(response)
            return errors, code

        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    response, code = automations_repository.automation(uuid=automation_uuid)
    if code == 200:
        automation = response['automation']
        return render_template('steps/step-new.html', form=form, automation=automation)

    return response['message'], code


@login_required.verify_login
def edit_step(automation_uuid, uuid):
    errors = []
    form = StepForm(request.form)
    if request.method == 'POST':
        args = form.data
        if form.validate_on_submit():

            args.pop('csrf_token')
            args.pop('submit')
            args.pop('uuid')

            response, code = automations_repository.edit_step(uuid=uuid, data=args)
            if code == 200:
                return 'Etapa editada com sucesso', code

            errors = convert_error_to_tuple(response)
            return errors, code

        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    response, code = automations_repository.step(uuid=uuid)
    if code == 200:
        step = response['step']
        response, code = automations_repository.automation(uuid=automation_uuid)
        if code == 200:
            automation = response['automation']
            step['topic'] = str(step['topic']).replace(automation['acronym'] + '_', '')
            form = StepForm(**step)
            return render_template('steps/step-edit.html', form=form, automation=automation)

    return response['message'], code


@login_required.verify_login
def view_step(uuid):
    response, code = automations_repository.step(uuid=uuid)
    if code == 200:
        step = response['step']
        automation = step['automation']
        step['topic'] = str(step['topic']).replace(automation['acronym'] + '_', '')
        return render_template('steps/step-view.html', step=step, automation=automation)

    return response['message'], code


def detail_step(uuid):
    response, code = automations_repository.step(uuid=uuid)
    if code == 200:
        step = response['step']
        automation = step['automation']
        step['topic'] = str(step['topic']).replace(automation['acronym'] + '_', '')
        return render_template('steps/step-detail.html', step=step, automation=automation)

    return response['message'], code


@login_required.verify_login
def delete_step(uuid):
    response, code = automations_repository.delete_step(uuid=uuid)
    return response['message'], code


#### FIELDS ####
@login_required.verify_login
def page_fields(step_uuid):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)

    response, code = automations_repository.fields(step_uuid=step_uuid, page=page, per_page=per_page, search=search)
    if code == 200:
        fields = response['fields']
        pagination = response['pagination']
        if len(fields) > 0:
            step = fields[0]['step']
            automation = step['automation']
        else:
            response, code = automations_repository.step(uuid=step_uuid)
            if code == 200:
                step = response['step']
                automation = step['automation']

        return render_template('fields/fields-list.html', fields=fields, pagination=pagination, step=step, automation=automation)

    return response['message'], code


@login_required.verify_login
def new_field(step_uuid):
    errors = []
    step = {}
    automation = {}
    form = FieldForm(request.form)

    if request.method == 'POST':
        args = form.data
        if form.validate_on_submit():

            args.pop('csrf_token')
            args.pop('submit')
            args.pop('uuid')

            response, code = automations_repository.new_field(step_uuid=step_uuid, data=args)
            if code == 201:
                return 'Campo criado com sucesso', code

            errors = convert_error_to_tuple(response)
            return errors, code

        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    response, code = automations_repository.step(uuid=step_uuid)
    if code == 200:
        step = response['step']
        automation = step['automation']
        return render_template('fields/field-new.html', form=form, step=step, automation=automation)

    return response['message'], code


@login_required.verify_login
def edit_field(uuid):
    errors = []
    form = FieldForm(request.form)
    if request.method == 'POST':
        args = form.data
        if form.validate_on_submit():

            args.pop('csrf_token')
            args.pop('submit')
            args.pop('uuid')

            response, code = automations_repository.edit_field(uuid=uuid, data=args)
            if code == 200:
                return 'Campo editado com sucesso', code

            errors = convert_error_to_tuple(response)
            return errors, code

        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    response, code = automations_repository.field(uuid=uuid)
    if code == 200:
        field = response['field']
        step = field['step']
        automation = step['automation']
        form = FieldForm(**field)
        return render_template('fields/field-edit.html', form=form, step=step, automation=automation)

    return response['message'], code


@login_required.verify_login
def delete_field(uuid):
    response, code = automations_repository.delete_field(uuid=uuid)
    return response['message'], code


### ITEMS ###
@login_required.verify_login
def items_by_automation(automation_uuid):
    return render_template('items/items.html')


@login_required.verify_login
def page_items_by_automation(automation_uuid):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    automation = return_automation(automation_uuid)
    steps = return_steps(automation)
    if len(steps) > 0:
        fields = return_fields(steps[0])
    else:
        fields = []

    response, code = automations_repository.items_by_automation(automation_uuid=automation_uuid, page=page, per_page=per_page)
    if code == 200:
        items = response['items']
        pagination = response['pagination']
        return render_template('items/items-by-automation-list.html', items=items, pagination=pagination, automation=automation, fields=fields)

    return response['message'], code


@login_required.verify_login
def page_items(step_uuid):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)

    response, code = automations_repository.step(uuid=step_uuid)

    if code == 200:
        step = response['step']

    response, code = automations_repository.automation(uuid=step['automation']['uuid'])
    if code == 200:
        automation = response['automation']
        steps = return_steps(automation)
        fields = return_fields(step)

    response, code = automations_repository.items_by_step(step_uuid=step_uuid, page=page, per_page=per_page, search=search)
    if code == 200:
        items = response['items']
        pagination = response['pagination']
        return render_template('items/items-list.html', items=items, pagination=pagination, automation=automation, step=step, fields=fields)

    return response['message'], code


@login_required.verify_login
def new_item(step_uuid):
    errors = []

    if request.method == 'POST':
        data = request.form

        args = data.to_dict()

        args.pop('csrf_token')
        args.pop('uuid')

        filtered_args = {key: value for key, value in args.items()}

        for key, value in filtered_args.items():
            if value == '':
                #errors.append((key, [f'O {key.replace("_", " ").upper()} é obrigatório']))
                args.pop(key)

        data = {'data': args}

        if not any(value for value in data['data'].values()):
            return 'Nenhum campo preenchido', 400

        response, code = automations_repository.new_item_by_step(step_uuid=step_uuid, data=data)
        if code == 201:
            return response['item'], code

        errors = convert_error_to_tuple(response)
        return errors, code
    else:

        response, code = automations_repository.step(uuid=step_uuid)
        if code == 200:
            step = response['step']
            automation = step['automation']
            steps = return_steps(automation)
            fields = return_fields(step)

            dynamic_fields = create_dynamic_fields(fields)
            form_class = type('ItemForm', (ItemForm,), dynamic_fields)
            form = form_class()
            for field_name, field_instance in dynamic_fields.items():
                setattr(form, field_name, field_instance)

            return render_template('items/item-new.html', form=form, automation=automation, step_uuid=step['uuid'])

    return response['message'], code


@login_required.verify_login
def edit_item(uuid):
    errors = []

    if request.method == 'POST':
        data = request.form

        args = data.to_dict()

        args.pop('csrf_token')
        args.pop('uuid')

        filtered_args = {key: value for key, value in args.items()}

        for key, value in filtered_args.items():
            if value == '':
                args.pop(key)

        data = {'data': args}

        response, code = automations_repository.edit_item(uuid=uuid, data=data)
        if code == 200:
            return response['item'], code

        errors = convert_error_to_tuple(response)
        return errors, code

    else:
        response, code = automations_repository.item(uuid=uuid)
        if code == 200:
            item = response['item']
            step = item['step']
            automation = step['automation']
            steps = return_steps(automation)
            fields = return_fields(step)

            dynamic_fields = create_dynamic_fields(fields)
            form_class = type('ItemForm', (ItemForm,), dynamic_fields)
            form = form_class(**item)
            for field_name, field_instance in dynamic_fields.items():
                setattr(form, field_name, field_instance)

            return render_template('items/item-edit.html', form=form, automation=automation, step_uuid=step['uuid'])

        return response['message'], code


@login_required.verify_login
def view_item(uuid):
    response, code = automations_repository.item(uuid=uuid)
    if code == 200:
        item = response['item']
        step = item['step']
        automation = step['automation']

        return render_template('items/item-view.html', item=item)

    return response['message'], code


@login_required.verify_login
def detail_item(uuid):
    response, code = automations_repository.item(uuid=uuid)
    if code == 200:
        item = response['item']
        step = item['step']
        automation = step['automation']
        steps = return_steps(automation)
        fields = return_fields(step)

        return render_template('items/item-detail.html', item=item, fields=fields)

    return response['message'], code


@login_required.verify_login
def delete_item(uuid):
    response, code = automations_repository.delete_item(uuid=uuid)
    return response['message'], code



### HISTORIC ###
@login_required.verify_login
def page_historic(item_uuid):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    response, code = automations_repository.item(uuid=item_uuid)
    if code == 200:
        item = response['item']
        step = item['step']
        automation = step['automation']

    response, code = automations_repository.historic(item_uuid=item_uuid, page=page, per_page=per_page)
    if code == 200:
        historic = response['history']
        pagination = response['pagination']
        return render_template('historic/historic-list.html', historic=historic, pagination=pagination, item=item)

    return response['message'], code

