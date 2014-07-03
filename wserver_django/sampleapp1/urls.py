from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'sampleapp1.views.hello'),
    url(r'^sleep', 'sampleapp1.views.test_sleep'),
    url(r'^media/(.*)$', 'sampleapp1.views.sampleapp1_media'),
    )