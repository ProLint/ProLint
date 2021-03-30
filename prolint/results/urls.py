from django.urls import path
from django.apps import apps

from .views import (
    TaskView,
    TaskViewRadar,
    ResultView,
    TaskViewDensity,
    TaskViewNetwork,
    TaskView3Ddensity,
    TaskViewThickcurv,
    ResultsListView,
    DeleteTask,
    ResultPublishView,
    DownloadTask,
    TaskViewLine,
    NoUserResults,
    NoUserResultsListView,
    FindResultsView,
)

from .scatter_handler import scatter_handler
from .radar_handler import radar_handler
from .density_handler import density_handler
from .line_handler import line_handler

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bokeh.server.django import document, autoload

bokeh_app_config = apps.get_app_config('bokeh.server.django')

# TODO: The application names are ugly
urlpatterns = [
    path('', FindResultsView.as_view(), name='find_result'),
    path('<username>/<str:task_id>/all/', NoUserResults.as_view(), name='results_detail'),
    path('<username>/<str:task_id>/', NoUserResultsListView.as_view(), name='all_results_list'),
    path('<username>/delete/<str:task_id>/', DeleteTask.as_view(), name='delete_task'),
    path('<username>/download/<str:task_id>/', DownloadTask.as_view(), name='download_task'),
    path("<username>/scatter/<str:task_id>/", TaskView.as_view(), name='task1'),
    path("<username>/radar/<str:task_id>/", TaskViewRadar.as_view(), name='task2'),
    path("<username>/density/<str:task_id>/", TaskViewDensity.as_view(), name='task3'),
    path("<username>/network/<str:task_id>/", TaskViewNetwork.as_view(), name='task4'),
    path("<username>/3ddensity/<str:task_id>/", TaskView3Ddensity.as_view(), name='task5'),
    path("<username>/thickcurv/<str:task_id>/", TaskViewThickcurv.as_view(), name='task6'),
    path("<username>/line/<str:task_id>/", TaskViewLine.as_view(), name='task7'),
    path("publish/<username>/<str:task_id>/", ResultPublishView.as_view(), name="publish"),
]

bokeh_apps = [
    autoload("scatter/", scatter_handler),
    autoload("radar/", radar_handler),
    autoload("density/", density_handler),
    autoload("line/", line_handler),
]

urlpatterns += staticfiles_urlpatterns()
