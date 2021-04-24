import os
from re import findall
from celery import uuid
from .models import FileMD
from .forms import FileMDForm
from django.views import View
from django.conf import settings
from calcul.tasks import calcul_contacts
from django.shortcuts import render, redirect


class UploadDataView(View):

    def get(self, request):
        form = FileMDForm()
        return render(request, 'uploads/submit.html', { 'form' : form })

    def post(self, request):

        # We don't need users for the webserver
        # so we just use a default user.
        username = 'prolint'
        model = FileMD
        form = FileMDForm(request.POST, request.FILES)

        # check the form is valid
        context = {}
        if form.is_valid():
            user = form.save(commit=False)
            user.user = request.user
            user.task_id_id = request.user.id
            user.save()

            task_id = user.task_id

            # Where to upload the data
            upload_dir = os.path.join(settings.USER_DATA, username, task_id)

            # The names of the uploaded files
            traj_path = request.FILES['traj'].name
            coor_path = request.FILES['coor'].name

            print ('#' * 20)
            print (form.cleaned_data.get('email'))
            # print (request.POST.)
            print ('#' * 20)

            user_inputs = dict(
                proteins=[x.strip(' ') for x in request.POST.get('prot_name').split(',') if len(x.strip(' ')) != 0], # list of strings (no whitespace)
                group_lipids=form.cleaned_data.get('group'), # boolean
                chains=form.cleaned_data.get('chains'), # boolean
                radii=[float(x) / 10 for x in form.cleaned_data.get('radii')], # list of floats
                lipids=findall(r"[\w']+", request.POST.get('lipids')), # list of strings (no whitespace)
                resolution=form.cleaned_data.get('resolution'), # string
                apps=request.POST.getlist('apps'),  # list of strings
                email=form.cleaned_data.get('email'), # string
                )

            # Exec task asynchronously
            task = calcul_contacts.apply_async((
                traj_path,
                coor_path,
                username,
                task_id,
                upload_dir,
                user_inputs
                ), task_id=task_id)

            context['task_id'] = task_id
            context['task_status'] = task.status
            context['media_url'] = settings.MEDIA_URL

            return redirect("/results/" + username + '/' + task_id, context)

        context['from'] = form

        return redirect("/uploads/")
