from django.urls import path

from .views import HomePageView, TutorialView, AnalysisView, VisualizationView, ContactUsView, WhyProLintView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('documentation/tutorial', TutorialView.as_view(), name='tutorial'),
    path('documentation/analysis_reference', AnalysisView.as_view(), name='anref'),
    path('documentation/visualization_reference', VisualizationView.as_view(), name='visref'),
    path('contact-us', ContactUsView.as_view(), name='contact'),
    path('documentation/purpose', WhyProLintView.as_view(), name='whyprolint'),
]
