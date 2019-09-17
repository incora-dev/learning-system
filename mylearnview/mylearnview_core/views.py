from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from collections import OrderedDict
from cloudinary.api import Error as CloudinaryError

from mylearnview.mylearnview_core.models import Course, Module, Page, StudentPageHistory, StudentPageNote
from mylearnview.mylearnview_core.forms import ModuleAddForm, CourseForm, CustomPageAddForm,\
    PageUpdateForm, ImagePageAddForm, ModuleUpdateForm
from .tasks import make_images_from_pdf
from .mixins import StudentCourseAccessMixin, ManagerPermission


@login_required
def index(request):
    return redirect(reverse('home'))


class CourseListView(TemplateView):
    """ Display all Courses """
    model = Course
    template_name = "app/courses_list.html"
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.get_manager_permission() or user.is_superuser:
            context['available'] = Course.objects.all().order_by('id')
        else:
            context['available'] = Course.objects.filter(student_acesses__student__id__contains=user.pk)
            context['closed'] = Course.objects.exclude(student_acesses__student__id__contains=user.pk)
        return context


class CourseCreateView(ManagerPermission, CreateView):
    """ Create new Course """
    model = Course
    template_name = "app/course_add.html"
    form_class = CourseForm

    def form_valid(self, form):
        new_course = form.save(commit=False)
        new_course.created_by = self.request.user
        new_course.save()
        messages.success(self.request, 'Course successfully Added')
        return HttpResponseRedirect(reverse('home'))

    def get_success_url(self):
        return reverse('home')


class CourseUpdateView(ManagerPermission, UpdateView):
    """ Update existing Course """
    model = Course
    template_name = "app/course_update.html"
    form_class = CourseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        context['course'] = context['object']
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Course successfully Updated')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')


class CourseDeleteView(ManagerPermission, DeleteView):
    """ Delete existing Course """
    model = Course

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'Course successfully Deleted')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('home')


class ModuleListView(StudentCourseAccessMixin, TemplateView):
    """ Display all Modules """
    model = Module
    template_name = "app/modules_list.html"

    def get(self, request, *args, **kwargs):
        """ Reorder logic for modules """
        
        request_reorder = self.request.GET.get('reorder')
        request_module = self.request.GET.get('module')
        if request_reorder and request_module:
            cur_module = Module.objects.filter(id=int(request_module))
            cur_sort_index = cur_module.first().sort_index
            if request_reorder == "up":
                Module.objects.filter(
                    sort_index=cur_sort_index-1,
                    course=kwargs['course_id']).update(sort_index=cur_sort_index)
                cur_module.update(sort_index=cur_sort_index-1)
            elif request_reorder == "down":
                Module.objects.filter(
                    sort_index=cur_sort_index+1,
                    course=kwargs['course_id']).update(sort_index=cur_sort_index)
                cur_module.update(sort_index=cur_sort_index+1)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(id=kwargs['course_id'])
        modules = Module.objects.filter(course=course).order_by('sort_index')
        context['page_obj'] = modules
        context['course'] = course
        context['first_module'] = modules.first()
        context['last_module'] = modules.last()
        return context


class ModuleCreateView(ManagerPermission, CreateView):
    """ Create new Module """
    model = Module
    template_name = "app/module_add.html"
    form_class = ModuleAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(id=self.kwargs['course_id'])
        return context

    def form_valid(self, form):
        cur_course = Course.objects.get(id=self.kwargs['course_id'])
        new_module = form.save(commit=False)
        new_module.created_by = self.request.user
        new_module.course = cur_course
        if new_module.pdf_file:
            if "pdf" in new_module.pdf_file.content_type:
                try:
                    new_module.save()
                except CloudinaryError:
                    form.add_error('pdf_file', 'PDF file is broken')
                    return render(self.request, self.template_name, {'form': form, 'course': cur_course})
                else:
                    make_images_from_pdf.delay(new_module.id)
            else:
                form.add_error('pdf_file', 'Invalid type of file')
                return render(self.request, self.template_name, {'form': form, 'course': cur_course})
        else:
            new_module.save()
        messages.success(self.request, 'Module successfully Added')
        return HttpResponseRedirect(reverse('module_detail',
            kwargs={'course_id': cur_course.id, 'module_id': new_module.id}))


class ModuleUpdateView(ManagerPermission, UpdateView):
    """ Update existing Module """
    model = Module
    template_name = "app/module_update.html"
    form_class = ModuleUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        cur_module = context['object']
        context['module'] = cur_module
        context['course'] = cur_module.course
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Module successfully Updated')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course_detail',
            kwargs={'course_id': self.kwargs['course_id']})


class ModuleDeleteView(ManagerPermission, DeleteView):
    """ Delete existing Module """
    model = Module

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'Module successfully Deleted')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('course_detail',
            kwargs={'course_id': self.kwargs['course_id']})


class ModuleDetailView(StudentCourseAccessMixin, TemplateView):
    """ Module detail """
    model = Module
    template_name = "app/module_detail.html"

    def dispatch(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        module_id = kwargs.get('module_id')
        self.object = get_object_or_404(self.model, course__id=course_id, pk=module_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """ Logic for change expand of page """
        request_expand = request.GET.get('expand')
        if request_expand:
            request.user.expand_type = request_expand
            request.user.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur_user = self.request.user

        if self.object.pages_ready:
            module_pages = self.object.pages.order_by('sort_index')
            paginator = Paginator(module_pages, per_page=1)
            page_obj = paginator.page(self.get_page().sort_index)
            context['page_obj'] = page_obj
            context['paginator'] = paginator
            context['notes'] = cur_user.notes.filter(page=page_obj[0]).order_by('-created_datetime')
        context['module'] = self.object
        context['course'] = self.object.course

        return context

    def post(self, request, *args, **kwargs):
        if request.POST['inputNote'].strip():
            page = StudentPageHistory.objects.filter(module=kwargs['module_id']).order_by('id').last().last_page
            note = StudentPageNote(
                student=request.user,
                page=page,
                note=request.POST['inputNote'],
                coord=request.POST.get('coord'),
            )
            note.save()
        return HttpResponseRedirect(reverse('module_detail',
            kwargs={'course_id': kwargs['course_id'], 'module_id': kwargs['module_id']} ))

    def get_page(self):
        """ Function gets Module and return
            last viewed page by user. If user move to
            other page of module, function will save to DB
            last viewed page.
        """
        module_pages = Page.objects.filter(module=self.object).order_by('sort_index')

        page_history = StudentPageHistory.objects.filter(module=self.object, student=self.request.user).last()
        if page_history:
            request_page = self.request.GET.get('page')
            if request_page:
                try:
                    page = module_pages.get(sort_index=request_page)
                except (Page.DoesNotExist, ValueError):
                    pass
                else:
                    self.save_history(self.object, page)
                    return page
            return module_pages.get(sort_index=page_history.last_page.sort_index)
        else:
            page = module_pages[0]
            self.save_history(self.object, page)
            return page

    def save_history(self, cur_module, page):
        cur_user = self.request.user
        page_history = StudentPageHistory.objects.filter(student=cur_user, module=cur_module, last_page=page)
        if page_history:
            page_history.delete()
        cur_history = StudentPageHistory(
            student=cur_user,
            module=cur_module,
            last_page=page
        )
        cur_history.save()
        return True


class StudentPageNoteUpdateView(StudentCourseAccessMixin, UpdateView):
    model = StudentPageNote
    http_method_names = ['post']
    fields = ['note', ]

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset().filter(student=self.request.user)

        self.module_id = self.kwargs.get('module_id')
        note_id = self.kwargs.get('note_id')
        note = get_object_or_404(queryset, page__module__course=self.course, page__module__id=self.module_id, pk=note_id)
        return note

    def form_valid(self, form):
        print('Hello')
        print(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        print('Hello')
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('module_detail', kwargs={"course_id":self.course.id, "module_id": self.module_id})


class StudentPageNoteDeleteView(StudentCourseAccessMixin, DeleteView):
    model = StudentPageNote

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset().filter(student=self.request.user)

        self.module_id = self.kwargs.get('module_id')
        note_id = self.kwargs.get('note_id')
        note = get_object_or_404(queryset, page__module__course=self.course, page__module__id=self.module_id, pk=note_id)
        return note

    def get_success_url(self):
        return reverse('module_detail', kwargs={"course_id":self.course.id, "module_id": self.module_id})


class ModuleOverviewView(StudentCourseAccessMixin, TemplateView):
    """ Module overview """
    model = Module
    template_name = "app/module_overview.html"

    def get(self, request, *args, **kwargs):
        """ Reorder logic for pages """
        request_reorder = self.request.GET.get('reorder')
        request_page = self.request.GET.get('page_id')
        if request_reorder and request_page:
            cur_page = Page.objects.filter(id=int(request_page))
            cur_sort_index = cur_page.first().sort_index
            if request_reorder == "up":
                Page.objects.filter(
                    sort_index=cur_sort_index-1,
                    module=kwargs['module_id']).update(sort_index=cur_sort_index)
                cur_page.update(sort_index=cur_sort_index-1)
            elif request_reorder == "down":
                Page.objects.filter(
                    sort_index=cur_sort_index+1,
                    module=kwargs['module_id']).update(sort_index=cur_sort_index)
                cur_page.update(sort_index=cur_sort_index+1)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur_user = self.request.user
        cur_module = Module.objects.get(id=kwargs['module_id'])
        if cur_module.pages_ready:
            pages = Page.objects.filter(module=cur_module).order_by('sort_index')
            student_notes = StudentPageNote.objects.filter(
                student=cur_user,
                page__module=cur_module)
            pages_history_list = StudentPageHistory.objects.filter(
                student=cur_user, module=cur_module).values_list('last_page__sort_index', flat=True)
            page_notes = OrderedDict()
            for page in pages:
                page_notes[page] = student_notes.filter(page=page).count()
            context['pages_list'] = page_notes
            context['first_page'] = pages.first()
            context['last_page'] = pages.last()
            context['pages_history'] = pages_history_list
        context['module'] = cur_module
        context['course'] = cur_module.course
        return context


class PageUpdateView(ManagerPermission, UpdateView):
    model = Page
    template_name = 'app/page_update.html'
    form_class = PageUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)
        page = context['object']
        cur_module = page.module
        cur_course = cur_module.course
        context['module'] = cur_module
        context['course'] = cur_course
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Page successfully Updated')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('module_overview',
            kwargs={'course_id': self.kwargs['course_id'], 'module_id': self.kwargs['module_id']})


class PageDeleteView(ManagerPermission, DeleteView):
    model = Page

    def delete(self, request, *args, **kwargs):
        cur_page = self.get_object()
        cur_page_sort_index = cur_page.sort_index
        cur_module = cur_page.module
        pages = Page.objects.filter(module=cur_module, sort_index__gt=cur_page_sort_index)
        cur_page.delete()
        pages.update(sort_index=F('sort_index') - 1)

        success_url = self.get_success_url()
        messages.success(self.request, 'Page successfully Deleted')
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('module_overview',
            kwargs={'course_id': self.kwargs['course_id'], 'module_id': self.kwargs['module_id']})


class ImagePageCreateView(ManagerPermission, UpdateView):
    """ Create new Image Pages from PDF file """
    model = Module
    template_name = "app/page_img_add.html"
    form_class = ImagePageAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur_module = context['object']
        context['module'] = cur_module
        context['course'] = cur_module.course
        return context

    def form_valid(self, form):
        cur_module = Module.objects.get(id=self.kwargs['pk'])
        cur_course = cur_module.course
        upload_pdf = self.request.FILES.get('pdf_file', False)
        if not upload_pdf:
            form.add_error('pdf_file', 'PDF file is required field')
            return render(self.request, self.template_name, {'form': form, 'course': cur_course, 'module': cur_module})
        if "pdf" in upload_pdf.content_type:
            try:
                cur_module.pdf_file = upload_pdf
                cur_module.save()
            except CloudinaryError:
                form.add_error('pdf_file', 'PDF file is broken')
                return render(self.request, self.template_name, {'form': form,
                                                                 'course': cur_course, 'module': cur_module})
            else:
                make_images_from_pdf.delay(cur_module.id)
                messages.success(self.request, 'Page successfully Added')
                return HttpResponseRedirect(reverse('module_detail',
                    kwargs={'course_id': cur_course.id, 'module_id': cur_module .id}))
        else:
            form.add_error('pdf_file', 'Invalid type of file')
            return render(self.request, self.template_name, {'form': form, 'course': cur_course, 'module': cur_module})


class CustomPageCreateView(ManagerPermission, CreateView):
    """ Create new Custom Page """
    model = Page
    template_name = "app/page_custom_add.html"
    form_class = CustomPageAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur_module = Module.objects.get(id=self.kwargs['module_id'])
        context['module'] = cur_module
        context['course'] = cur_module.course
        return context

    def form_valid(self, form):
        cur_module = Module.objects.get(id=self.kwargs['module_id'])
        cur_course = cur_module.course
        new_page = form.save(commit=False)
        new_page.module = cur_module
        new_page.pagetype = 'custom'
        new_page.sort_index = Page.objects.filter(module=cur_module).count() + 1
        new_page.save()

        cur_module.pages_ready = True
        cur_module.save()
        messages.success(self.request, 'Page successfully Added')
        return HttpResponseRedirect(reverse('module_detail',
            kwargs={'course_id': cur_course .id, 'module_id': cur_module.id}))
