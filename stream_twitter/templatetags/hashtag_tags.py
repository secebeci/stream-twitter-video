from django import template
from stream_django.enrich import Enrich
from stream_django.feed_manager import feed_manager

enricher = Enrich()

register = template.Library()
 
@register.simple_tag
def render_hashtag(hashtag):
    html = '<div class="hashtag"><a href="{link}">{hashtag}</a></div>'\
        .format(hashtag=hashtag.name, link="/hashtag/{0}"
                .format(hashtag.name))
    return html

@register.inclusion_tag('stream_twitter/notifications.html')
def show_notification(user):
    feed = feed_manager.get_notification_feed(user.user.id)
    activities = feed.get(limit=30)['results']
   # user = activities.activities.actor
    enriched_activities = enricher.enrich_aggregated_activities(activities)

    context = {
        'enriched_activities': enriched_activities,

    }
    return context