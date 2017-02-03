from django.forms import ModelForm
from stream_twitter.models import Follow, Tweet
from django import forms
#from haystack.forms import SearchForm

# class TweetSearchForm(SearchForm):

# 	def no_query_found(self):
# 		return self.searchqueryset.all()



class FollowForm(ModelForm):

    class Meta:
        exclude = set()
        model = Follow

class TweetForm(ModelForm):

	class Meta:
		exclude = ["created_at"]
		model = Tweet