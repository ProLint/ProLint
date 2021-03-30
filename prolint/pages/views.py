from django.views.generic import TemplateView

#TODO: make this D-R-Y
class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class TutorialView(TemplateView):
    template_name = 'pages/tutorial.html'

class AnalysisView(TemplateView):
    template_name = 'pages/analysisRef.html'

class VisualizationView(TemplateView):
    template_name = 'pages/visualizationRef.html'

class ContactUsView(TemplateView):
    template_name = 'pages/contact-us.html'

class WhyProLintView(TemplateView):
    template_name = 'pages/whyprolint.html'