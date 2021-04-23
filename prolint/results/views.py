import os
# django imports
from django.views.generic import DetailView, ListView
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse

# celery
from celery import current_app

# bokeh
from bokeh.embed import server_document

from uploads.models import FileMD
from users.models import CustomUser


def task_user(task_id):
    """
    Get the user who submitted the task.
    """
    obj = FileMD.objects.filter(task_id=task_id)
    obj_user = CustomUser.objects.filter(id=obj.get().user_id)
    return obj_user.get().username


class ResultView(DetailView):
    def get(self, request, username, task_id):

        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        # Check if the user asking to view the task is the same as the one who submitted it.
        if request.user.username != task_user(task_id):
            # A different user can only view the results if they are published.
            if len(ExploreResults.objects.filter(task_id=task.id)) == 0:
                return JsonResponse(response_data)

        task_list = ['task1',     'task5',    'task4',    'task6',      'task7',    'task3',  'task2']
        app_list = ['Scatter', '3D Density', 'Network', 'ThickCurv', 'TimeSeries', 'Density', 'Radar']

        app_description = [
            'Lipid-protein interactions visualized as a complete scatter plot where each point represents the interaction of one residue with a particular lipid.',
            'NGL Viewer based application to visualize pre-calclated 3D densities and projected contact heatmaps on the surface of proteins.',
            'Lipids and proteins are represented as nodes and their interactions with each other as edges.Edge width relates to interaction magnitude.',
            'Three.js based application showing the thickness and curvature induced by membrane proteins in their surrounding lipid environment.',
            'Timeseries information of the most prominent contacts.',
            'Calculates 2D densities with live updates allowing the user to change stylistic properties as well as fine-tune other options.',
            'Application for the detailed comparison of individual residues with respect to their interactions with lipids. Six different parameters are compared using a radar chart.'
        ]

        app_info = zip(task_list, app_list, app_description)

        if task.status == 'SUCCESS':
            return render(request, "results/calculated_vizapps_overview.html", dict(task_id=task_id, username=username, app_info=app_info))

        return JsonResponse(response_data)


class NoUserResults(DetailView):
    def get(self, request, username, task_id):

        user_uploads = FileMD.objects.filter(task_id=task_id)

        user_uploads = list(user_uploads)
        user_uploads.reverse()

        user_uploads_w_status = []
        for fmd in user_uploads:
            if fmd.status == "DELETED":
                continue
            task = current_app.AsyncResult(fmd.task_id)
            if fmd.status != task.status:
                fmd.status = task.status
                fmd.save()

            user_uploads_w_status.append(fmd)

        if len(user_uploads) == 1:
            task = user_uploads[0]
        else:
            return JsonResponse(dict(ErrorReturn="Could not find the requested ID!."))

        celery_task = current_app.AsyncResult(task.task_id)

        if len(user_uploads) == 0:
            return render(request, "results/nouser_upload.html", {'user_uploads' : user_uploads_w_status, 'username' : username})

        response_data = {'task_status': task.status, 'task_id': task.id}


        if task.status != 'SUCCESS':
            return JsonResponse(response_data)
        else:
            # Order has to match the definition of APPS_CALCULATED_SUCCESSFULLY used by celery
            # TODO: make this dynamic and independent of the order of any of the items.
            task_list = ['task1',     'task7',    'task5',    'task4',      'task6',    'task3',  'task2']
            image_list = ['Scatter', 'TimeSeries', '3D Density', 'Network', 'Thickness & Curvature', 'Density', 'Radar']
            app_list = ['Point Distribution', 'Distance Lines', 'Heatmap Viewer', 'Network Graph', 'Thickness & Curvature', 'Density Distribution', 'Metric Comparison']
            status_list = [boolean for boolean in celery_task.result['errors'].values()]

            app_description = [
                'Interactions visualized as a point plot where each point represents the interaction of one residue with a particular lipid.',
                'Distance timeseries for the most high-scoring lipid-protein contacts',
                'Interactive 3D visualization of lipid densities and projected contact heatmaps onto the surface of proteins.',
                'Lipids/proteins are represented as collapsible/expandible nodes and their interactions with each other as edges.',
                'The changes that proteins induce in their surrounding lipid environment are displayed using thickness and curvature mesh files.',
                'Real-time interactive 2D densities.',
                'Per residue comparison of calculated contact metrics. Employs an interactive radar plot to display values.'
            ]

            app_info = zip(task_list, app_list, app_description, status_list, image_list)

            return render(request, "results/calculated_vizapps_overview.html", dict(task_id=task_id, username=username, app_info=app_info))


from django.template.defaulttags import register
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def list_items(string):
    if isinstance(string, str):
        el = string.split('\n')
        el = [x for x in el if len(x) != 0]
        return el
    else:
        return string
class NoUserResultsListView(ListView):
    def get(self, request, username, task_id):

        submission = FileMD.objects.filter(task_id=task_id)
        if len(submission) == 1:
            submission = submission[0]
        else:
            return JsonResponse(dict(ErrorReturn="Could not find the requested ID!."))

        celery_task = current_app.AsyncResult(submission.task_id)
        setattr(submission, 'result', celery_task.result)
        user_uploads = FileMD.objects.filter(task_id=task_id)

        # Show newest first
        user_uploads = list(user_uploads)
        user_uploads.reverse()

        user_uploads_w_status = []
        for fmd in user_uploads:
            if fmd.status == "DELETED":
                continue
            task = current_app.AsyncResult(fmd.task_id)
            if fmd.status != task.status:
                fmd.status = task.status
                fmd.save()

            user_uploads_w_status.append(fmd)

        if os.path.isfile(os.path.join('media', 'user-data', username, task_id, 'logs.log')):
            fh = open(os.path.join('media', 'user-data', username, task_id, 'logs.log'), 'r').read()
            return render(request, "results/nouser_upload.html", {'user_uploads' : user_uploads_w_status, 'submission': submission, 'username' : username, 'logs': fh})
        elif os.path.isfile(os.path.join('media', 'user-data', username, task_id, 'progress.log')):
            fh = open(os.path.join('media', 'user-data', username, task_id, 'progress.log'), 'r').read()
            return render(request, "results/nouser_upload.html", {'user_uploads' : user_uploads_w_status, 'submission': submission, 'username' : username, 'logs': fh})
        else:
            return render(request, "results/nouser_upload.html", {'user_uploads' : user_uploads_w_status, 'submission': submission, 'username' : username})


from .forms import FindResultForm
class FindResultsView(View):
    def get(self, request):

        form = FindResultForm()
        return render(request, 'results/find_task_id.html', { 'form' : form })

    def post(self, request):
        username = 'prolint'
        form = FindResultForm(request.POST)

        if form.is_valid():

            task_id = request.POST.get('task_id')

            user_uploads = FileMD.objects.filter(task_id=task_id)
            if user_uploads.count() == 0:
                return render(request, "404.html")
            elif user_uploads[0].status == "DELETED":
                return render(request, "404.html")

            user_uploads = list(user_uploads)
            user_uploads.reverse()

            user_uploads_w_status = []
            for fmd in user_uploads:
                if fmd.status == "DELETED":
                    continue
                task = current_app.AsyncResult(fmd.task_id)
                if fmd.status != task.status:
                    fmd.status = task.status
                    fmd.save()

                user_uploads_w_status.append(fmd)

            return render(request, "results/nouser_upload.html", {'user_uploads' : user_uploads_w_status, 'username' : username})

        else:
            form = FindResultForm()
            return render(request, 'results/find_task_id.html', { 'form' : form })


class ResultsListView(ListView):
    def get(self, request, username):

        user_uploads = FileMD.objects.filter(user_id=request.user.id)

        # Show newest first
        user_uploads = list(user_uploads)
        user_uploads.reverse()

        user_uploads_w_status = []
        for fmd in user_uploads:
            if fmd.status == "DELETED":
                continue
            task = current_app.AsyncResult(fmd.task_id)
            if fmd.status != task.status:
                fmd.status = task.status
                fmd.save()

            user_uploads_w_status.append(fmd)

        return render(request, "results/user_uploads_list.html", {'user_uploads' : user_uploads_w_status, 'username' : username})


from explore.forms import ExploreResultsForm
from explore.models import ExploreResults
class ResultPublishView(View):
    def get(self, request, username, task_id):
        form = ExploreResultsForm()
        obj = FileMD.objects.filter(task_id=task_id)[0]

        if len(ExploreResults.objects.filter(task_id=task_id)) != 0:
            return JsonResponse(dict(ErrorReturn="You already published the results."))

        file_names = []
        file_names.append(obj.traj.url.split('/')[-1])
        file_names.append(obj.coor.url.split('/')[-1])
        radii = [float(x) for x in obj.radii]

        upload_data = dict(title=obj.title, prot_name=obj.prot_name, scatter=obj.scatter,
                            lipids=obj.lipids, radii=radii, file_names=file_names)

        return render(request, 'results/results_publish.html', { 'form' : form, 'upload_data': upload_data})


    def post(self, request, username, task_id):
        model = ExploreResults
        filemd_model = FileMD.objects.filter(task_id=task_id)[0]

        form = ExploreResultsForm(request.POST, request.FILES)

        if form.is_valid():
            current_user = CustomUser.objects.filter(pk=request.user.id)
            form.instance.user = current_user[0]

            form.instance.title = filemd_model.title
            form.instance.task_id = filemd_model.task_id
            form.instance.prot_name = filemd_model.prot_name
            form.instance.scatter = filemd_model.scatter
            form.instance.radii = filemd_model.radii

            form.save()

            return redirect("/explore")

        context['from'] = form

        return render(request, 'results/results_publish.html', context)

class DeleteTask(DetailView):
    def post(self, request, username, task_id):

        # FileMD.objects.filter(task_id=task_id).delete()
        task = FileMD.objects.get(task_id=task_id)
        task.delete()

        #TODO: deleted objects should also get deleted from the Explore view.
        # current_user = CustomUser.objects.filter(pk=request.user.id)
        # current_user_id = current_user.get().id
        # user_uploads = FileMD.objects.filter(user_id=current_user_id)

        # return render(request, "results/user_uploads_list.html", {'user_uploads' : user_uploads, 'username' : username})
        return redirect("/")


class DownloadTask(View):
    def post(self, request, username, task_id):
        import os
        import shutil
        from django.http import HttpResponse, Http404

        prefix = 'media/user-data/' + username + '/' + task_id
        destination = 'media/downloads'

        shutil.make_archive(os.path.join(destination, f'ProLint_{task_id[:8]}'), 'zip', prefix)
        with open(os.path.join(destination, f'ProLint_{task_id[:8]}.zip'), 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-binary")
            response['Content-Disposition'] = 'inline; filename=' + f'ProLint_{task_id[:8]}.zip'
            return response
        raise Http404


class TaskViewRadar(View):
    def get(self, request, username, task_id):
        return radar(request, task_id, username)

class TaskViewLine(View):
    def get(self, request, username, task_id):
        return line(request, task_id, username)

class TaskView(View):
    def get(self, request, username, task_id):

        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            return scatter(request, task.id, username)

        return JsonResponse(response_data)

class TaskViewDensity(View):
    def get(self, request, username, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            return density(request, task.id, username)

        return JsonResponse(response_data)

class TaskViewNetwork(View):
    def get(self, request, username, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        response_data['radii'] = task.result['radii']
        response_data['prot_name'] = task.result['prot_name']
        response_data['username'] = username
        response_data['app'] = 'Network Graph'

        proteins, metrics, radii = [], [], []
        import os
        from django.conf import settings
        for netfile in os.listdir(os.path.join(settings.USER_DATA, username, task_id, '.')):
            if netfile.endswith('network.json'):
                prot, metric, radius, _ = netfile.split('__')
                if prot not in proteins:
                    proteins.append(prot)
                if metric not in metrics:
                    metrics.append(metric)
                if radius not in radii:
                    radii.append(radius)

        netfiles = {
            'proteins': proteins,
            'metrics': metrics,
            'radii': radii

            }
        response_data['netfiles'] = netfiles

        if task.status == 'SUCCESS':
            return render(request, "results/network.html", response_data)

        return JsonResponse(response_data)


class TaskView3Ddensity(View):
    def get(self, request, username, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}#, 'task_result_og': task.result}

        try:
            metrics = task.result['metrics']
            html_metrics = "<script>var metrics = ["
            for tr in metrics:
                html_metrics = html_metrics + "'" + tr + "', "
            html_metrics = html_metrics + "];</script>"
        except:
            html_metrics = '<script>var metrics = [];</script>'

        task_result = task.result['lipid_groups']
        html_result = "<script>var task_result = ["
        for tr in task_result:
            html_result = html_result + "'" + tr + "', "
        html_result = html_result + "];</script>"

        import os
        from django.conf import settings
        key = os.path.join(settings.USER_DATA, username, task_id, 'data.json')

        if os.path.isfile(key):
            response_data['density_only'] = 'true'
        else:
            response_data['density_only'] = 'false'


        response_data["task_result"] = html_result
        response_data["metrics"] = html_metrics
        response_data["prot_name"] = task.result['prot_name']
        response_data["username"] = username
        response_data['radii'] = task.result['radii']
        response_data["app"] = 'Heatmap & Density Viewer'

        if task.status == 'SUCCESS':
            return render(request, "results/heatmap_density.html", response_data)

        return JsonResponse(response_data)


class TaskViewThickcurv(View):
    def get(self, request, username, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        response_data["prot_name"] = task.result['prot_name']
        response_data["username"] = username
        response_data["app"] = 'Thickness & Curvature'

        if task.status == 'SUCCESS':
            return render(request, "results/thickcurv.html", response_data)

        return JsonResponse(response_data)



def scatter(request, task_id, username):
    script = server_document(request._current_scheme_host + "/scatter", arguments=dict(task_id=task_id, username=username))
    return render(request, "results/embed_points.html", dict(script=script, app='Point Distribution'))

def radar(request, task_id, username):
    script = server_document(request._current_scheme_host + "/radar", arguments=dict(task_id=task_id, username=username))
    return render(request, "results/embed_radar.html", dict(script=script, app='Metric Comparison'))

def density(request, task_id, username):
    script = server_document(request._current_scheme_host + "/density", arguments=dict(task_id=task_id, username=username))
    return render(request, "results/embed_density.html", dict(script=script, app='Density Distribution'))

def line(request, task_id, username):
    script = server_document(request._current_scheme_host + "/line", arguments=dict(task_id=task_id, username=username))
    return render(request, "results/embed_distances.html", dict(script=script, app='Distance Lines'))
