# -*- coding: utf-8 -*-
"""
Snippet template tags
"""
from django_feedparser import settings
from django import template
from django.utils.safestring import mark_safe
from django_feedparser.utils import FeedparserError, get_feed_renderer
import datetime

register = template.Library()

@register.simple_tag(takes_context=True)
def feedparser_render(context, url, *args, **kwargs):
    """
    Render a feed and return its builded html
    
    Usage: ::
    
        {% feedparser_render 'http://localhost/sample.xml' %}
    
    Or with all accepted arguments: ::
    
        {% feedparser_render 'http://localhost/sample.xml' renderer='CustomRenderer' template='foo/custom.html' expiration=3600 %}
    """
    renderer_name = kwargs.get('renderer', settings.FEED_DEFAULT_RENDERER_ENGINE)
    renderer_template = kwargs.get('template', None)
    expiration = kwargs.get('expiration', 0)

    renderer = get_feed_renderer(settings.FEED_RENDER_ENGINES, renderer_name)
    return renderer().render(context, url, template=renderer_template, expiration=expiration)

@register.filter
def feed_date(value):
    try:
        return datetime.datetime(*value[:6])
    except:
        pass
