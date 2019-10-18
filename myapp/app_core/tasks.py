from celery import task
from .models import Page, Module
import cloudinary.api

@task
def make_images_from_pdf(module_id):
    """ Function gets Module and convert
        each page from pdf file to png image """
    cur_module = Module.objects.get(id=module_id)
    cur_module.pages_ready = False
    cur_module.save()
    num_exist_pages = Page.objects.filter(module=module_id).count()
    module_api = cloudinary.api.resource(cur_module.pdf_file.public_id, pages=True)
    num_pages = module_api['pages']
    secure_url = module_api['secure_url']

    for n in range(num_pages):
        print(secure_url)
        cloud_img = cloudinary.uploader.upload(secure_url, page=n+1, format='png', density=175)
        new_page = Page(
            module=cur_module,
            image_file_reference=cloud_img['url'],
            pagetype='image',
            sort_index=num_exist_pages+n+1
        )
        new_page.save()
    if not cur_module.pages_ready:
        cur_module.pages_ready = True
        cur_module.save()
    cur_module.pages_ready = True
    cur_module.save()
    return True
