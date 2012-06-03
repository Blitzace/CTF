from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CTF.views.home', name='home'),
    # url(r'^CTF/', include('CTF.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^rpc/$', 'vrecords.views.rpc_handler'),
     url(r'^results/$', 'vrecords.views.results'),
     url(r'^results_pie.png$', 'vrecords.views.showResults'),

)
