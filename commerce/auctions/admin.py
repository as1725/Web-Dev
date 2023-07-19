from django.contrib import admin
from .models import *

# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "starting_bid", "image", "category", "active", "user", "winner")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "bid")
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "comment")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")
    
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "password", "email", "first_name", "last_name")

admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)