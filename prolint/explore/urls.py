from django.urls import path

from .views import ResultsExploreView, ResultView

urlpatterns = [
    path('', ResultsExploreView.as_view(), name="database"),
    path('', ResultsExploreView.as_view(), name="explore"),
    path('<username>/<str:task_id>/', ResultView.as_view(), name='explore_one'),
]
