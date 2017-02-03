from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.shortcuts import render_to_response, render, get_object_or_404,\
    redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.context import RequestContext
# from haystack.forms import SearchForm
# from haystack.generic_views import SearchView

from stream_django.enrich import Enrich
from stream_django.feed_manager import feed_manager
from stream_twitter.forms import FollowForm, TweetForm #, TweetSearchForm
from stream_twitter.models import Follow
from stream_twitter.models import Tweet, Hashtag 
from pytutorial import settings

from django.http import HttpResponseRedirect


enricher = Enrich()



class TimelineView(CreateView):
    model = Tweet
    fields = ['text','video','slide', 'myfile']
    success_url = "/timeline/"
    #form_class = TweetForm
    def form_valid(self, form):
        form.instance.user = self.request.user
        files= self.request.FILES.getlist('myfile')
        for f in files:
            form.instance.myfile = f 
        return super(TimelineView, self).form_valid(form)
 
    def get(self, request):
        feeds = feed_manager.get_news_feeds(request.user.id)
        acts = feeds.get('news_feed').get()['results']
        acts = enricher.enrich_activities(acts)
        hashtags = Hashtag.objects.order_by('-occurrences')
        #slides = Slideshare.objects.all()
        context = {
            'acts': acts,
            'form': self.get_form_class(),
            'login_user': request.user,
            'hashtags': hashtags,
           # 'slides' : slides,
        }
        return render(request, 'stream_twitter/timeline.html', context)

class CreateTweet(CreateView):
    form_class = TweetForm
    template_name = "stream_twitter/_tweetbox.html" 
    success_url = "/timeline/"


class HomeView(ListView):
   # model = Tweet
    def get(self, request):
        #if not request.user.is_authenticated() and not settings.USE_AUTH:
         #   admin_user = authenticate(
          #      username=settings.DEMO_USERNAME, password=settings.DEMO_PASSWORD)
           # auth_login(request, admin_user)
        context = RequestContext(request)
        tweets = Tweet.objects.all()    #.order_by('-id')[:20]

        #form = SearchForm(request.GET)
        #tweets = form.search()
        
        # termset = request.GET.get("q")
        # if termset:
        #     for term in termset.split(): 
        #         tweets = tweets.filter(
        #             Q(text__icontains=term) |
        #             Q(user__first_name__icontains=term)|
        #             Q(user__last_name__icontains=term)|
        #             Q(user__username__icontains=term)
        #             ).distinct()

        tweets = tweets.order_by('-id')[:20]
        context_dict = {
            'login_user': request.user,
            #'users': User.objects.order_by('date_joined')[:50]
            'tweets': tweets,
        }
        return render_to_response('stream_twitter/home.html', context_dict, context)


#class MySearchView(SearchView):
    #def get_queryset(self):
        #queryset = super(MySearchView, self).get_queryset()

def search(request):
    context = RequestContext(request)
    tweets = Tweet.objects.all()    #.order_by('-id')[:20]
    
    termset = request.GET.get("q")
    if termset:
        for term in termset.split(): 
            tweets = tweets.filter(
                Q(text__icontains=term) |
                Q(user__first_name__icontains=term)|
                Q(user__last_name__icontains=term)|
                Q(user__username__icontains=term)
                ).distinct()

    tweets = tweets.order_by('-id')[:20]

    context_dict = {
            'login_user': request.user,
            #'users': User.objects.order_by('date_joined')[:50]
            'tweets': tweets,
        }
    return render_to_response('stream_twitter/home.html', context_dict, context)




def get_tweet(request):
    form = TweetForm(request.POST)
    if form.is_valid():
        form.instance.user = request.user
        form.instance.user_id = request.user_id
    else:
        form = TweetForm()
    
    return redirect("/timeline/")

def follow(request):
    form = FollowForm(request.POST)
    if form.is_valid():
        follow = form.instance
        follow.user = request.user
        follow.save()
    return redirect("/discover/")



def unfollow(request, target_id):
    follow = Follow.objects.filter(user=request.user, target_id=target_id).first()
    if follow is not None:
        follow.delete()
    return redirect("/discover/")


def discover(request):
    #token = user.token #byme
    users = User.objects.order_by('date_joined')[:50]
    login_user = User.objects.get(username=request.user)
    following = []
    for i in users:
        if len(i.followers.filter(user=login_user.id)) == 0:
            following.append((i, False))
        else:
            following.append((i, True))
    login_user = User.objects.get(username=request.user)
    context = {
        'users': users,
        'form': FollowForm(),
        'login_user': request.user,
        'following': following
    }
    return render(request, 'stream_twitter/follow_form.html', context)


def user(request, user_name):
    user = get_object_or_404(User, username=user_name)
    feeds = feed_manager.get_user_feed(user.id)
    activities = feeds.get()['results']
    activities = enricher.enrich_activities(activities)
    context = {
        'activities': activities,
        'user': user,
        'login_user': request.user
    }
    return render(request, 'stream_twitter/user.html', context)


def hashtag(request, hashtag_name):
    hashtag_name = hashtag_name.lower()
    feed = feed_manager.get_feed('user', 'hash_%s' % hashtag_name)
    activities = feed.get(limit=25)['results']

    activities = enricher.enrich_activities(activities)
    context = {
        'hashtag_name': hashtag_name,
        'activities': activities
    }
    return render(request, 'stream_twitter/hashtag.html', context)
 

def notification(request, user_id):
    enricher = Enrich()

    feed = feed_manager.get_notification_feed(request.user.id)
    activities = feed.get(limit=30)['results']
   # user = activities.activities.actor
    enriched_activities = enricher.enrich_aggregated_activities(activities)

    context = {
        'enriched_activities': enriched_activities,

    }
    return render(request, 'stream_twitter/notifications.html', context)

