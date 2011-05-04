from django.conf.urls.defaults import *

urlpatterns = patterns('activities.views',
url(r'^user/(?P<page>\w+)$', 'user_activities', name="user_activities"),
url(r'^subscription/$', 'activity_subscriptions', name="activity_subscriptions"),
url(r'^test/$', 'activities_test', name="activities_test"),
)
