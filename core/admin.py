from django.contrib import admin
from .audit import AuditLog
from .moderation import ContentReport

admin.site.register(AuditLog)
admin.site.register(ContentReport)