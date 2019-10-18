from django.core.validators import FileExtensionValidator


from rest_framework import serializers

from cloudinary.api import Error as CloudinaryError

from myapp.app_core.models import Course, Module, Page, StudentPageNote
from myapp.app_core.tasks import make_images_from_pdf


class CourseSerializer(serializers.ModelSerializer):

    created_by = serializers.CharField(source='created_by.username', read_only=True)
    icon = serializers.FileField(
        use_url=True,
        allow_empty_file=True,
        required=False,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg'])]
    )

    class Meta:
        model = Course
        fields = '__all__'


class ModuleListSerializer(serializers.ModelSerializer):
    pdf_file = serializers.FileField(
        use_url=True,
        allow_empty_file=True,
        required=False,
        validators=[FileExtensionValidator(['pdf'])]
    )
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    last_opened = serializers.IntegerField(read_only=True)

    class Meta:
        model = Module
        fields = '__all__'


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleListSerializer(many=True, read_only=True)
    icon = serializers.FileField(
        use_url=True,
        allow_empty_file=True,
        required=False,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg'])]
    )
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class PageSerializer(serializers.ModelSerializer):
    image_file_reference = serializers.FileField(
        use_url=True,
        allow_empty_file=True,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg'])]
    )

    class Meta:
        model = Page
        exclude = ('module', )


class ModuleDetailSerializer(serializers.ModelSerializer):
    pdf_file = serializers.FileField(
        use_url=True,
        allow_empty_file=True,
        required=False,
        validators=[FileExtensionValidator(['pdf'])]
    )
    pages_count = serializers.IntegerField(source='pages.count', read_only=True)
    pages = PageSerializer(many=True, read_only=True)
    course_name = serializers.CharField(source='course.title', read_only=True)
    last_opened = serializers.IntegerField(read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Module
        fields = '__all__'
        extra_kwargs = {'created_by': {'read_only': True}, 'pages_ready': {'read_only': True}}

    def validate_pdf_file(self, val):
        if "pdf" not in val.content_type:
            raise serializers.ValidationError('It\'s not pdf file')
        return val

    def create(self, validated_data):
        pdf_file = validated_data.get('pdf_file')

        if pdf_file:
            try:
                module = Module.objects.create(**validated_data)
            except CloudinaryError:
                raise serializers.ValidationError('Load broken pdf file')
            else:
                make_images_from_pdf.delay(module.id)
        else:
            return super().create(validated_data)

        return module


class PageNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPageNote
        exclude = ('student', 'page')


class PageCreateSerializer(serializers.ModelSerializer):
    pdf_file = serializers.FileField(validators=[FileExtensionValidator(['pdf'])], write_only=True, required=False)
    image_file_reference = serializers.FileField(
        read_only=True,
        use_url=True,
        allow_empty_file=True,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg'])]
    )

    class Meta:
        model = Page
        fields = '__all__'
        extra_kwargs = {
            'module': {'read_only': True},
            'sort_index': {'read_only': True},
        }

    def create(self, validated_data):

        pdf_file = validated_data.pop('pdf_file', None)
        module = validated_data.get('module')
        if pdf_file:
            try:
                module.pdf_file = pdf_file
                module.save()
            except CloudinaryError:
                raise serializers.ValidationError('pdf_file', 'PDF file is broken')
            else:
                make_images_from_pdf.delay(module.id)
                return Page()
        return super().create(validated_data)


class PageDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='module.course.title', read_only=True)
    module_name = serializers.CharField(source='module.title', read_only=True)
    image_file_reference = serializers.FileField(
        use_url=True,
        allow_empty_file=True,
        validators=[FileExtensionValidator(['png', 'jpeg', 'jpg', 'svg'])]
    )

    class Meta:
        model = Page
        fields = '__all__'
        extra_kwargs = {'module': {'read_only': True}}