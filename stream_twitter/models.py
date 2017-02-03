from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.db.models import signals
from django.template.defaultfilters import slugify
from stream_django import activity
from stream_django.feed_manager import feed_manager
 
from pytutorial.settings import STREAM_PERSONAL_FEED
from embed_video.fields import EmbedVideoField #by me


def upload_location(instance, filename): # img dosyasinin directionini gosterir ona gore yer atar.
    return "files"

 
class Tweet(activity.Activity, models.Model):
    user = models.ForeignKey('auth.User')
    text = models.CharField(max_length=160)
    video = EmbedVideoField(blank=True)
    slide = EmbedVideoField(blank=True)
    #width_field = models.IntegerField( blank=True, default=100, null=True)
    #height_field= models.IntegerField( blank=True, default=100, null=True)
    myfile = models.FileField(upload_to = "files", 
                        null=True,
                        blank=True,
                        )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def print_self(self):
        print(self.text)

    @property
    def activity_object_attr(self):
        return self

    def save(self):
        self.create_hashtags()
        super(Tweet, self).save()
 
    def create_hashtags(self):
        hashtag_set = set(self.parse_hashtags())
        for hashtag in hashtag_set:
            h, created = Hashtag.objects.get_or_create(name=hashtag)
            h.save()
        Hashtag.objects.filter(name__in=hashtag_set).update(occurrences=F('occurrences')+1)

    def parse_hashtags(self):
        return [slugify(i) for i in self.text.split() if i.startswith("#")]

    def parse_mentions(self):
        mentions = [slugify(i) for i in self.text.split() if i.startswith("@")]
        return User.objects.filter(username__in=mentions)

    def parse_all(self):
        parts = self.text.split()
        hashtag_counter = 0
        mention_counter = 0
        result = {"parsed_text": "", "hashtags": [], "mentions": []}
        for index, value in enumerate(parts):
            if value.startswith("#"):
                parts[index] = "{hashtag" + str(hashtag_counter) + "}"
                hashtag_counter += 1
                result[u'hashtags'].append(slugify(value))
            if value.startswith("@"):
                parts[index] = "{mention" + str(mention_counter) + "}"
                mention_counter += 1
                result[u'mentions'].append(slugify(value))
        result[u'parsed_text'] = " ".join(parts)
        return result

    @property 
    def activity_notify(self):
        targets = [feed_manager.get_news_feeds(self.user_id)['news_feed']]
        
        for hashtag in self.parse_hashtags():
            targets.append(feed_manager.get_feed('user', 'hash_%s' % hashtag))
        for user in self.parse_mentions():
            targets.append(feed_manager.get_news_feeds(user.id)['news_feed'])
            #activity = { 'actor': self.user_id, 'verb': 'mention', 'object': user.id} #me
            #feed = feed_manager.get_notification_feed(user.id) #me
            #feed.add_activity(activity) #me
            targets.append(feed_manager.get_notification_feed(user.id)) #me 
        return targets


class Follow(activity.Activity, models.Model):
    user = models.ForeignKey('auth.User', related_name='friends')
    target = models.ForeignKey('auth.User', related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')

    @property
    def activity_author_feed(self): 
        return STREAM_PERSONAL_FEED

    @property
    def print_self(self):
        print(self.id)

    @property
    def activity_actor_attr(self):
        return (self.user)  #by me 

    @property
    def activity_actor_id(self):
        return self.activity_object_attr.pk

    @property
    def activity_object_attr(self):
        return (self.target)

    @property
    def activity_notify(self):
        return [feed_manager.get_notification_feed(self.target_id)]
         
########################################### added by secebeci ##########################################
# class Mention(activity.Activity, models.Model):
#     user = models.ForeignKey('auth.User', related_name='friends')
#     target = models.ForeignKey('auth.User', related_name='followers')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'target')

#     @property
#     def activity_author_feed(self): 
#         return STREAM_PERSONAL_FEED

#     @property
#     def print_self(self):
#         print(self.id)

#     @property
#     def activity_actor_attr(self):
#         return (self.user)  #by me 

#     @property
#     def activity_actor_id(self):
#         return self.activity_object_attr.pk

    # @property
    # def activity_object_attr(self):
    #     return (self.target)

    # @property
    # def activity_notify(self):
    #     return [feed_manager.get_notification_feed(self.target_id)]
         
############################################################################################################        
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    description = models.TextField()
    picture = models.ImageField(upload_to='profile_pictures', blank=True)


class Hashtag(models.Model):
    name = models.CharField(max_length=160)
    occurrences = models.IntegerField(default=0)


def unfollow_feed(sender, instance, **kwargs):
    feed_manager.unfollow_user(instance.user_id, instance.target_id)


def follow_feed(sender, instance, created, **kwargs):
    if created:
        feed_manager.follow_user(instance.user_id, instance.target_id)


signals.post_delete.connect(unfollow_feed, sender=Follow)
signals.post_save.connect(follow_feed, sender=Follow)
