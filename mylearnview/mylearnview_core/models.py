from django.db import models
from django.db.models import Subquery, OuterRef
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver

from cloudinary.models import CloudinaryField
from ckeditor_uploader.fields import RichTextUploadingField


class Course(models.Model):

    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name="Title")

    icon = CloudinaryField(
        blank=True,
        null=True)

    description = models.TextField(
        blank=True,
        verbose_name="Description")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name="Author")

    created_datetime = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return "%s" % (self.title, )


class Module(models.Model):

    course = models.ForeignKey(Course,
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Course",
        related_name='modules')

    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name="Title")

    sort_index = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name="Sort index",
        validators=[MinValueValidator(1)]
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description")

    pdf_file = CloudinaryField("PDF file",
        blank=True,
        null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name="Author")

    created_datetime = models.DateTimeField(
        auto_now_add=True)

    pages_ready = models.BooleanField(
        default=True,
        verbose_name="Page status")

    def __str__(self):
        return "%s (%s)" % (self.title, self.course)

    class Meta:
        ordering = ('-course__id', 'sort_index')


class Page(models.Model):

    module = models.ForeignKey(
        Module,
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name='pages'
    )

    types_of_page = (
        ('image', 'Image'),
        ('custom', 'Custom'),
    )

    pagetype = models.CharField(
        max_length=25,
        choices=types_of_page,
        blank=True)

    custom_content = RichTextUploadingField(
        blank=True)

    image_file_reference = CloudinaryField(
        max_length=256,
        blank=True,
        verbose_name="Reference to image")

    sort_index = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name="Sort index",
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return "%s pages in %s" % (self.sort_index, self.module)

    class Meta:
        ordering = ('-module__id', 'sort_index')


class StudentPageHistory(models.Model):

    student = models.ForeignKey(settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        verbose_name="Studet")

    module = models.ForeignKey(Module,
        blank=False,
        null=True,
        related_name='history',
        on_delete=models.CASCADE)

    last_page = models.ForeignKey(Page,
        blank=True,
        null=True,
        related_name='history_page',
        verbose_name="Last page")

    last_visited_datetime = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True)

    def __str__(self):
        return "History %s by %s" % (self.last_page, self.student)


class StudentPageNote(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        verbose_name="Student",
        related_name='notes'
    )

    page = models.ForeignKey(
        Page,
        blank=False,
        null=True,
        verbose_name="Page",
        related_name='notes'
    )

    created_datetime = models.DateTimeField(
        auto_now_add=True)

    note = models.TextField(
        blank=False,
        null=True,
        verbose_name="Note")

    coord = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Coordinate'
    )

    def __str__(self):
        return "Note for %s page in %s by %s" % (self.page.sort_index, self.page.module, self.student)

    class Meta:
        ordering = ('-created_datetime', )


class StudentCourseAccess(models.Model):
    """
    Get access for student to course
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_accesses",
        verbose_name="Student",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Course",
        related_name="student_acesses"
    )
    created_datetime = models.DateTimeField("Created datetime", auto_now_add=True)

    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Added by")

    def __str__(self):
        return "Course %s available for %s" % (self.student, self.course)


@receiver(pre_save, sender=Module)
def handle_change_module_index(sender, **kwargs):
    instance = kwargs.get('instance')

    try:
        course = instance.course
    except Course.DoesNotExist:
        course = None

    if course:
        module_count = instance.course.modules.count()

        # if instance not created yet
        if not instance.id:
            module_count += 1
            start_pos = module_count
        else:
            # if instance already exist get and set old sort_index value
            try:
                old_state = sender.objects.values('sort_index').get(pk=instance.pk)
            except sender.DoesNotExist:
                module_count += 1
                start_pos = module_count
            else:
                old_sort_index = old_state.get('sort_index')
                start_pos = old_sort_index

        end_pos = instance.sort_index
        # if set position bigger then count of modules
        # set index of last position
        if end_pos > module_count:
            end_pos = module_count
            instance.sort_index = end_pos
        elif end_pos < 1:
            end_pos = 1
            instance.sort_index = end_pos

        # calculate increment
        i = -1
        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
            i = 1

        print(start_pos, end_pos)
        # update sort indexes
        if start_pos != end_pos:
            instance.course.modules.filter(sort_index__gte=start_pos, sort_index__lte=end_pos).\
                update(sort_index=models.F('sort_index')+i)


@receiver(pre_save, sender=Page)
def handle_change_page_index(sender, **kwargs):
    instance = kwargs.get('instance')

    try:
        module = instance.module
    except Module.DoesNotExist:
        module = None

    if module:
        pages_count = instance.module.pages.count()

        # if instance not created yet
        if not instance.id:
            pages_count += 1
            start_pos = pages_count
        else:
            # if instance already exist get and set old sort_index value
            try:
                old_state = sender.objects.values('sort_index').get(pk=instance.pk)
            except sender.DoesNotExist:
                pages_count += 1
                start_pos = pages_count
            else:
                old_sort_index = old_state.get('sort_index')
                start_pos = old_sort_index

        end_pos = instance.sort_index
        # if set position bigger then count of modules
        # set index of last position
        if end_pos > pages_count:
            end_pos = pages_count
            instance.sort_index = end_pos
        elif end_pos < 1:
            end_pos = 1
            instance.sort_index = end_pos

        # calculate increment
        i = -1
        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
            i = 1

        # update sort indexes
        if start_pos != end_pos:
            instance.module.pages.filter(sort_index__gte=start_pos, sort_index__lte=end_pos). \
                update(sort_index=models.F('sort_index')+i)
