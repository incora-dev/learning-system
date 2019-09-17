from django.forms import ModelForm, CharField

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from mylearnview.mylearnview_core.models import Module, Course, Page


class CourseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})


    class Meta:
        model = Course
        fields = ['title', 'icon', 'description']


class ModuleAddForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['sort_index'].widget.attrs.update({'class': 'form-control'})
        self.fields['pdf_file'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Module
        fields = ['title', 'sort_index', 'pdf_file',
         'description']
        help_texts = {
            'pdf_file': 'If pdf file is uploaded, the pages from the pdf will be converted to pages in the module.\
                         If no pdf is uploaded, you can add pages manually later.',
        }


class ModuleUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['sort_index'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Module
        fields = ['title', 'sort_index', 'description']


class PageUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['module'].widget.attrs.update({'class': 'form-control'})
        self.fields['pagetype'].widget.attrs.update({'class': 'form-control'})
        self.fields['custom_content'].widget.attrs.update({'class': 'form-control'})
        self.fields['image_file_reference'].widget.attrs.update({'class': 'form-control'})
        self.fields['sort_index'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Page
        fields = ['module', 'pagetype', 'custom_content', 'image_file_reference', 'sort_index']


class ImagePageAddForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pdf_file'].required = True
        self.fields['pdf_file'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Module
        fields = ['pdf_file']


class CustomPageAddForm(ModelForm):
    custom_content = CharField(
        widget=CKEditorUploadingWidget(),
        required=True)

    class Meta:
        model = Page
        fields = ['custom_content']
