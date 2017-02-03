import datetime
from haystack import indexes
from .models import Hashtag 
 
class HashtagIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	name = indexes.CharField(model_attr='name')
	#occurrences = indexes.IntegerField(model_attr='occurrences')
	#created_at = indexes.DateTimeField(model_attr='created_at')

	def get_model(self):
		return Hashtag


	def index_queryset(self, using=None):
		"""Used when the entire index for model is updated"""
		return self.get_model().objects.all() #filter(created_at__lte = datetime.datetime.now()) 

