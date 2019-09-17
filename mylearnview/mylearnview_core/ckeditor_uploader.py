from ckeditor_uploader.views import ImageUploadView, get_upload_filename
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import cloudinary
from ckeditor_uploader import image_processing, utils


class CustomImageUploadView(ImageUploadView):
    def post(self, request, **kwargs):
        """
        Uploads a file and send back its URL to CKEditor.
        """
        uploaded_file = request.FILES['upload']

        backend = image_processing.get_backend()

        ck_func_num = request.GET.get('CKEditorFuncNum')
        if ck_func_num:
            ck_func_num = escape(ck_func_num)

        # Throws an error when an non-image file are uploaded.
        if not getattr(settings, 'CKEDITOR_ALLOW_NONIMAGE_FILES', True):
            try:
                backend.image_verify(uploaded_file)
            except utils.NotAnImageException:
                return HttpResponse("""
                    <script type='text/javascript'>
                    window.parent.CKEDITOR.tools.callFunction({0}, '', 'Invalid file type.');
                    </script>""".format(ck_func_num))

        saved_path = self._save_file(request, uploaded_file)
        if str(saved_path).split('.')[1].lower() != 'gif':
            self._create_thumbnail_if_needed(backend, saved_path)

        url = saved_path
        if ck_func_num:
            # Respond with Javascript sending ckeditor upload url.
            return HttpResponse("""
            <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({0}, '{1}');
            </script>""".format(ck_func_num, url))
        else:
            retdata = {'url': url, 'uploaded': '1',
                       'fileName': uploaded_file.name}
            return JsonResponse(retdata)

    @staticmethod
    def _save_file(request, uploaded_file):
        filename = get_upload_filename(uploaded_file.name, request.user)

        img_name, img_format = os.path.splitext(filename)
        IMAGE_QUALITY = getattr(settings, "IMAGE_QUALITY", 60)
        if str(img_format).lower() == "png":

            img = Image.open(uploaded_file)
            img = img.resize(img.size, Image.ANTIALIAS)
            saved_path = default_storage.save("{}.jpg".format(img_name), uploaded_file)
            img.save("{}.jpg".format(img_name), quality=IMAGE_QUALITY, optimize=True)

        elif str(img_format).lower() == "jpg" or str(img_format).lower() == "jpeg":

            img = Image.open(uploaded_file)
            img = img.resize(img.size, Image.ANTIALIAS)
            saved_path = default_storage.save(filename, uploaded_file)
            img.save(saved_path, quality=IMAGE_QUALITY, optimize=True)

        else:
            cloud_img = cloudinary.uploader.upload(uploaded_file)
            saved_path = cloud_img['url']
        return saved_path


upload = csrf_exempt(CustomImageUploadView.as_view())