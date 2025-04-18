from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'landing_page',
            'submit-requests',
            'register',
            'login',
            'challenges_faced',
            'data_modeling',
            'data_pipelines',
            'cloud_setup',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'landing_page':
            return 1.0  # Highest priority for the homepage
        elif item in ['challenges_faced', 'data_modeling', 'data_pipelines', 'cloud_setup', 'submit-requests']:
            return 0.9
        elif item in ['register', 'login']:
            return 0.8
        return 0.5  # Default priority for other pages

    def changefreq(self, item):
        if item == 'landing_page':
            return 'daily'  # Homepage changes frequently
        return 'weekly'  # Default frequency

    def lastmod(self, item):
        if item == 'landing_page':
            return datetime(2025, 4, 18)  # Replace with dynamic logic if available
        return None  # Default: no last modified date