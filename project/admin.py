from django.contrib import admin
from project.models import User
from project.models import Transaction
from project.models import KnowledgeBase

admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(KnowledgeBase)

