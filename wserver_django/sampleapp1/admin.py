# -*- coding: utf-8 -*-

from django.contrib import admin

# Register your models here.
from sampleapp1.models import Person, Car
 
class PersonAdmin(admin.ModelAdmin):
    list_display = ["name", "desc", ]
    # search_fields http://my.oschina.net/u/1032854/blog/193277
    search_fields = ["name", "desc", ]

class CarAdmin(admin.ModelAdmin):
    # 使用包含外键的字段的 list_display ,list_display包含函数名, 同时下面需要一个同名函数
    list_display = ["name", "owner", "get_owner_desc", ] # 这里用下划线分割,页面展示使用空格分割
    search_fields = ["name", ]
    
    def get_owner_desc(self, obj):
        return obj.owner.desc
 
admin.site.register(Person, PersonAdmin)
admin.site.register(Car, CarAdmin)