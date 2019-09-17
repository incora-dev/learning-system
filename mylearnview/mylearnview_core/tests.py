from django.test import TestCase, Client
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from .models import StudentCourseAccess, Course

# Create your tests here.

User = get_user_model()


class CourseListViewTest(TestCase):
    fixtures = ['demodb.json']
    url = reverse('home')

    def setUp(self):
        self.client_student = Client()
        self.client_student.login(username='dev1@ya.ru', password='1234567a')

        self.client_manager = Client()
        self.client_manager.login(username='dev@ya.ru', password='1234567a')

        self.client_none = Client()

    def test_student_access(self):
        response = self.client_student.get(self.url)

        self.assertEqual(response.context['available'].count(), 1)
        self.assertEqual(response.context['closed'].count(), 2)

        student_id = self.client_student.session['_auth_user_id']
        manager_id = self.client_manager.session['_auth_user_id']

        StudentCourseAccess.objects.create(student_id=student_id, course_id=2, added_by_id=manager_id)

        response = self.client_student.get(self.url)
        self.assertEqual(response.context['available'].count(), 2)
        self.assertEqual(response.context['closed'].count(), 1)

    def test_manager_access(self):
        all_courses = Course.objects.all()
        response = self.client_manager.get(self.url)

        self.assertEqual(response.context['available'].count(), all_courses.count())

    def test_unauthorized_access(self):
        response = self.client_none.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url='%s?next=/library'%reverse('login'))

    def test_post_requset(self):
        response = self.client_manager.post(self.url)
        self.assertEqual(response.status_code, 405)

        response = self.client_student.post(self.url)
        self.assertEqual(response.status_code, 405)

        response = self.client_none.post(self.url)
        self.assertRedirects(response, expected_url='%s?next=/library' % reverse('login'))