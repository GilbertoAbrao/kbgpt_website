import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import ValidationError, inlineformset_factory
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from requests import Response, post

from .forms import FileUploadForm, LoginForm, RegisterForm, BotForm, BotFileForm, QAForm
from .models import FileModel, BotModel, BotFileModel


def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            # save new user
            user = form.save(commit=False)
            user.email = user.username
            user.save()

            # search for group whit the same name as the user.username
            # if it exists, add the user to the group
            # if it doesn't exist, create the group and add the user to it
            if not user.groups.filter(name=user.username).exists():
                group = Group.objects.create(name=user.username)
                user.groups.add(group)
            else:
                group = Group.objects.get(name=user.username)
                user.groups.add(group)

            # do login
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
            )

            return redirect('main')

        else:

            return render(request, 'register.html', {'form': form})

    elif request.method == 'GET':

        form = RegisterForm()

        return render(request, 'register.html', {'form': form})


def login_page_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                # messages.info = (request,f'Hello {user.username}! You have been logged in')
                return redirect('main')
            else:
                messages.info(request, 'Username or password is incorrect!')
                # logout_view(request)
    return render(
        request, 'login.html', context={'form': form, 'message': messages})


class MainTemplateView(TemplateView):
    template_name = "main.html"


def upload_file_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            name = file.name
            owner = request.user
            # if user is in a group, set group to the first group they are in
            if request.user.groups.all().exists():
                group = request.user.groups.all()[0].name
            else:
                group = None
            path = file
            file_obj = FileModel.objects.create(name=name, owner=owner, path=path, group=group)
            # Perform any additional processing or actions here
            return redirect('file_detail', pk=file_obj.pk)
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})




@login_required
def chatbot_list_view(request):

    template = 'bot_list.html'
    url_list_name = 'chatbot_list_url'
    url_create_name = 'chatbot_create_url'
    url_update_name = 'chatbot_update_url'
    url_delete_name = 'chatbot_delete_url'
    page_number = request.GET.get('p', '1')
    page_limit = request.GET.get('l', '25')
    search = request.GET.get('s', None)

    if search:
        # get all BotModels of the same group as the user
        object_list = BotModel.objects.filter(group=request.user.groups.all()[0], name__icontains=search)
    else:
        object_list = BotModel.objects.filter(group=request.user.groups.all()[0])

    if not page_limit.isdigit():
        page_limit = '25'
    else:
        if int(page_limit) > 100:
            page_limit = '100'

    if not page_number.isdigit():
        page_number = '1'

    if not (page_limit.isdigit() and int(page_limit) > 0):
        page_limit = '25'

    paginator = Paginator(object_list, page_limit)

    try:
        page = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page = paginator.page(1)

    context = {
        'object_list': page,
        'url_list_name': url_list_name,
        'url_create_name': url_create_name,
        'url_update_name': url_update_name,
        'url_delete_name': url_delete_name,
        'list_rows_per_page': ['10', '25', '50', '100'],
        'rows_per_page': str(page.paginator.per_page),
    }

    return render(request, template, context)


@login_required
def chatbot_create_view(request):
    
    template = 'bot_detail.html'
    url_list_name = 'chatbot_list_url'
    url_update_name = 'chatbot_update_url'
    url_delete_name = 'chatbot_delete_url'

    match request.method:
        
        case 'GET':

            form = BotForm()
            
            context = {
                'url_list_name': url_list_name,
                'url_delete_name': url_delete_name,
                'form': form,
            }

            return render(request, template, context)

        case 'POST':

            form = BotForm(request.POST or None)

            if form.is_valid():

                bot = form.save(commit=False)
                bot.owner = request.user
                bot.group = request.user.groups.all()[0]
                bot.save()
                return redirect(url_list_name)
            
            else:

                context = {
                    'url_list_name': url_list_name,
                    'url_delete_name': url_delete_name,
                    'form': form,
                }

                return render(request, template, context)
            

@login_required
def chatbot_update_view(request, pk):

    template = 'bot_detail.html'
    url_list_name = 'chatbot_list_url'
    url_delete_name = 'chatbot_delete_url'
    obj = get_object_or_404(BotModel, id=pk)
    child_create_url = 'chatbot_document_create_url'
    child_object_list = None
    child_paginator = None
    child_page = None

    match request.method:

        case "GET":
            
            form = BotForm(request.POST or None, instance=obj)
            file_upload_form = FileUploadForm()
            

            # if update bot, get all BotFileModels of this bot
            if not form.instance.id is None:
                page_number = request.GET.get('p', '1')
                page_limit = request.GET.get('l', '25')
                search = request.GET.get('s', None)
                if search:
                    # get all BotFileModels of this bot
                    child_object_list = BotFileModel.objects.filter(bot_id=obj.id, name__icontains=search).order_by('id')
                else:
                    child_object_list = BotFileModel.objects.filter(bot_id=obj.id).order_by('id')
                
                if not page_limit.isdigit():
                    page_limit = '25'
                else:
                    if int(page_limit) > 100:
                        page_limit = '100'

                if not page_number.isdigit():
                    page_number = '1'

                if not (page_limit.isdigit() and int(page_limit) > 0):
                    page_limit = '25'

                child_paginator = Paginator(child_object_list, page_limit)

                try:
                    child_page = child_paginator.page(page_number)
                except (EmptyPage, PageNotAnInteger):
                    child_page = child_paginator.page(1)


            context = {
                'url_list_name': url_list_name,
                'url_delete_name': url_delete_name,
                "form": form,
                "file_upload_form": file_upload_form,

                # child list
                "child_create_url": child_create_url,
                "child_object_list": child_object_list,
                'child_object_list': child_page,
            }

            return render(request, template, context)

        case "POST":
            
            form = BotForm(request.POST or None, request.FILES or None, instance=obj)
            form_bot_file_factory = inlineformset_factory(BotModel, BotFileModel, form=BotFileForm, extra=1)
            form_bot_file = form_bot_file_factory(request.POST or None, request.FILES or None, instance=obj)

            if form.is_valid() and form_bot_file.is_valid():
                bot = form.save()
                form_bot_file.instance.bot = bot
                form_bot_file.save()

            context = {
                'url_list_name': url_list_name,
                'url_delete_name': url_delete_name,
                "form": form,
                "form_bot_file": form_bot_file,

                # child list
                "child_create_url": child_create_url,
                "child_object_list": child_object_list,
                'child_object_list': child_page,
            }
            return render(request, template, context)




@login_required
def chatbot_delete_view(request, pk):

    template = 'delete.html'
    obj = get_object_or_404(BotModel, id=pk)
    url_list_name = 'chatbot_list_url'
    url_update_name = 'chatbot_update_url'

    if request.method == 'GET':
        # after deleting redirect to

        context = {
            "obj": obj,
            "return_url": url_update_name,
        }

        return render(request, template, context)

    elif request.method == "POST":

        obj.delete()

        return redirect(url_list_name)




@login_required
def chatbot_document_create_view(request, pk):
    
    bot = get_object_or_404(BotModel, id=pk)

    if request.method == 'POST':

        form = FileUploadForm(request.POST, request.FILES)

        try: 
            valid = form.is_valid()
        except ValidationError as e:
            valid = False
            form.add_error(None, e)
            return redirect('chatbot_update_url', pk=pk)
        

        
        if valid:
            file = form.cleaned_data['file']
            name = file.name
            
            path = file
            file_obj = BotFileModel.objects.create(bot=bot, name=name, path=path)

            # fill callback_url on file_obj
            file_obj.callback_url = f"{ request.build_absolute_uri('/') }chatbot/{bot.id}/document/{ str(file_obj.uuid) }/webhook/"
            file_obj.save()

            # send to api backend to injestion
            headers = {
                'Content-Type': 'application/json',
            }

            payload = [
                {
                    "file_path": f"{settings.MEDIA_ROOT}{str(file_obj.path)}",
                    "index_name": str(bot.uuid),
                    "callback_url": file_obj.callback_url,
                },
            ]

            response: Response = post(f'{ settings.API_BACKEND_URL }/ingestion/pinecone', headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                messages.success(request, f'File {file_obj.name} uploaded successfully!')
            else:
                messages.error(request, f'Error uploading file {file_obj.name}: {response.text}')

                # delete file from database
                file_obj.delete()
        
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error uploading file: {error}')

        return redirect('chatbot_update_url', pk=pk)
    
    


@csrf_exempt
def chatbot_document_webhook_view(request, pk, uuid):

    if request.method == 'POST':

        bot = get_object_or_404(BotModel, id=int(pk))

        # get file from database by bot.id and bot_file.uuid
        file = get_object_or_404(BotFileModel, bot_id=bot.id, uuid=uuid)

        # get payload from request
        payload = json.loads(request.body)

        # update file status
        file.status = payload['status']
        file.save()



@login_required
def qa_view(request):

    template_name = 'qa.html'
    url_list_name = 'main'

    if request.method == 'GET':

        form = QAForm()

        bot_id = request.GET.get('bot_id')

        if bot_id:
            bot = get_object_or_404(BotModel, id=bot_id)
            form.fields['bot'] = bot
        
        context = {
            "url_list_name": url_list_name,
            "form": form,
        }

        return render(request, template_name, context=context)



    elif request.method == 'POST':

        form = QAForm(request.POST)

        if form.is_valid():

            bot = form.cleaned_data['bot']
            question = form.cleaned_data['question']

            headers = {
                'Content-Type': 'application/json',
            }

            payload = {
                "index_name": str(bot.uuid),
                "question": question,
            }

            response: Response = post(f'{ settings.API_BACKEND_URL }/qa/pinecone', headers=headers, data=json.dumps(payload))

            if response.status_code == 200:

                #messages.success(request, f'Question answered successfully!')

                context = {
                    "url_list_name": url_list_name,
                    "form": form,
                    "answer": response.json()['answer'],
                }
                return render(request, template_name, context=context)
            
            else:
            
                messages.error(request, f'Error answering question: {response.text}')
                context = {
                    "url_list_name": url_list_name,
                    "form": form,
                }
                return render(request, template_name, context=context)


        else:

            return render(request, 'register.html', {'form': form})

    
