from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from stream_twitter import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from filebrowser.sites import site
import ckeditor_uploader.urls
import haystack.urls 

urlpatterns = patterns('',
  url(r'^accounts/', include('allauth.urls')),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^discover/', login_required(views.discover)),
  url(r'^timeline/',
     login_required(views.TimelineView.as_view())),
  url(r'^create/',
     login_required(views.CreateTweet.as_view()), name='create'), #byme
  url(r'^user/(?P<user_name>.+)/$', views.user),
  url(r'^(?P<user_id>\d+)/notifications/$', views.notification, name='notifications'),
  url(r'^hashtag/(?P<hashtag_name>.+)/', views.hashtag),
  url(r'^$', views.HomeView.as_view()),
  url(r'^follow/$', login_required(views.follow), name='follow'),
  url(r'^unfollow/(?P<target_id>\d+)/$', login_required(views.unfollow), name='unfollow'),
  #url(r'^slideshows/', include('slideshows.urls', namespace='slideshows')), #by me
  url(r'^grappelli/', include('grappelli.urls')),
  url(r'^admin/filebrowser/', include(site.urls)), #by me
  url(r'^admin/ckeditor/', include('ckeditor_uploader.urls')), #by me
  #url(r'^search/', include('haystack.urls')), #by me
  url(r'^search/', views.search, name='search'), #by me


) 

urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns(
    'django.views.static',
    (r'media/(?P<path>.*)',
     'serve',
     {'document_root': settings.MEDIA_ROOT}))
