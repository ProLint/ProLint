from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render#, redirect
# from django.http import JsonResponse

# from .forms import ExploreResultsForm
from .models import ExploreResults

# from uploads.models import FileMD
# from users.models import CustomUser
from celery import current_app


class ResultsExploreView(View):
    def get(self, request):
        model = ExploreResults.objects.all()

        return render(request, 'explore/explore_all.html', {'model': model})

class ResultView(DetailView):
    def get(self, request, username, task_id):

        username = 'prolint'

        # task = current_app.AsyncResult(task_id)
        # response_data = {'task_status': task.status, 'task_id': task.id}

        # Check if the user asking to view the task is the same as the one who submitted it.
        # if request.user.username != task_user(task_id):
        #     if len(ExploreResults.objects.filter(task_id=task.id)) == 0:
        #         return JsonResponse(response_data)

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

        desc = ExploreResults.objects.filter(task_id=task_id)[0].description
        # if task.status == 'SUCCESS':
        return render(request, "results/all_results.html", dict(task_id=task_id, username=username, app_info=app_info))
        # return render(request, "explore/explore_one.html", dict(task_id=task_id, username=username, desc=desc, app_info=app_info))
            # return redirect( "/results/" + username + "/" + task_id, dict(task_id=task_id))

        # return JsonResponse(response_data)
