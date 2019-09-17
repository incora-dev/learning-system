from django.contrib import admin
from mylearnview.mylearnview_core.models import Course, Module, Page, StudentPageHistory, StudentPageNote, StudentCourseAccess


admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Page)
admin.site.register(StudentPageHistory)
admin.site.register(StudentPageNote)
admin.site.register(StudentCourseAccess)