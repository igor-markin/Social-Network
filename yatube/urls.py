from django.conf import settings
from django.conf.urls import handler404, handler500  # noqa
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework.authtoken import views

handler404 = 'posts.views.page_not_found'  # noqa
handler500 = 'posts.views.server_error'  # noqa

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('administrator/', admin.site.urls),
    path('api-token-auth/', views.obtain_auth_token),
    path('', include('posts.urls')),
    path('about/', include('about.urls'))
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve,
                        {'document_root': settings.MEDIA_ROOT, }), ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
