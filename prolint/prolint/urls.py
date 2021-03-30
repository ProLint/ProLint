from django.conf.urls.static import static

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

# import bokeh_apps #NEEDED HERE!
from results.urls import bokeh_apps

urlpatterns = [

    path('admin/', admin.site.urls),
    path('users/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('uploads/', include('uploads.urls')),
    path('results/', include('results.urls')),
    path('explore/', include('explore.urls')),
    path('calcul/', include('calcul.urls')),
    path('', include('pages.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns
