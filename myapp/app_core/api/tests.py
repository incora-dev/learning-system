import json

from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class CourseListCreateAPIViewTest(APITestCase):
    """
    Test for CourseList endpoint
    """
    fixtures = ['demodb.json']
    url = '/api/core/courses/'

    def setUp(self):
        self.manager_client = APIClient()
        self.student_client = APIClient()

        token = json.loads(self.manager_client.post('/api/accounts/login/', {'email': 'dev@ya.ru', 'password': '1234567a'}, format='json').content)
        self.manager_client.credentials(HTTP_AUTHORIZATION='JWT %s' % token['token'])

        token = json.loads(self.student_client.post('/api/accounts/login/', {'email': 'dev1@ya.ru', 'password': '1234567a'}).content)
        self.student_client.credentials(HTTP_AUTHORIZATION='JWT %s' % token['token'])

    def test_manager_permissions(self):
        resp = self.manager_client.get(self.url)
        data = json.loads(resp.content)

        self.assertIn('access', data)
        self.assertEqual(data['user_is_manager'], True)
        self.assertEqual(len(data['access']), 3)
        self.assertEqual(len(data['closed']), 0)

        resp = self.manager_client.post(self.url, data={'title': 'Test course'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_student_permissions(self):
        resp = self.student_client.get(self.url)
        data = json.loads(resp.content)

        self.assertIn('access', data)
        self.assertIn('user_is_manager', data)
        self.assertEqual(data['user_is_manager'], False)
        self.assertEqual(len(data['access']), 1)
        self.assertEqual(len(data['closed']), 2)

        resp = self.student_client.post(self.url, data={'title': 'Test course'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_permissons(self):
        anonymous_client = APIClient()

        resp = anonymous_client.get('/api/core/courses/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class CourserRetriveUpdateAPIViewTest(APITestCase):
    url = '/api/core/courses/%d/'
    fixtures = ['demodb.json']

    def setUp(self):
        self.manager_client = APIClient()
        self.student_client = APIClient()

        self.course_id1 = 1
        self.course_id2 = 2

        token = json.loads(self.manager_client.post('/api/accounts/login/', {'email': 'dev@ya.ru', 'password': '1234567a'}, format='json').content)
        self.manager_client.credentials(HTTP_AUTHORIZATION='JWT %s' % token['token'])

        token = json.loads(self.student_client.post('/api/accounts/login/', {'email': 'dev1@ya.ru', 'password': '1234567a'}).content)
        self.student_client.credentials(HTTP_AUTHORIZATION='JWT %s' % token['token'])

    def test_manager_permissions(self):
        resp = self.manager_client.get(self.url % self.course_id1)
        data = json.loads(resp.content)

        self.assertEqual(data['user_is_manager'], True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.manager_client.get(self.url % self.course_id2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        new_title = 'Python The Best'
        resp = self.manager_client.patch(self.url % self.course_id1, data={'title': new_title})
        data = json.loads(resp.content)

        self.assertEqual(data['title'], new_title)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_student_permissions(self):
        resp = self.student_client.get(self.url % self.course_id1)
        data = json.loads(resp.content)

        self.assertEqual(data['user_is_manager'], False)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.student_client.get(self.url % self.course_id2)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        new_title = 'Python The Best'
        resp = self.student_client.patch(self.url % self.course_id1, data={'title': new_title})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_permissions(self):
        anonymous_client = APIClient()

        resp = anonymous_client.get(self.url % self.course_id1)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = anonymous_client.patch(self.url % self.course_id1)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseModuleTestCase(APITestCase):
    fixtures = ['demodb.json']

    def setUp(self):
        self.manager_client = APIClient()
        self.student_client = APIClient()

        self.course_id1 = 1
        self.course_id2 = 2

        token = json.loads(self.manager_client.post('/api/accounts/login/', {'email': 'dev@ya.ru', 'password': '1234567a'}, format='json').content)
        self.manager_client.credentials(HTTP_AUTHORIZATION='JWT %s' % token['token'])

        token = json.loads(self.student_client.post('/api/accounts/login/', {'email': 'dev1@ya.ru', 'password': '1234567a'}).content)
        self.student_client.credentials(HTTP_AUTHORIZATION='JWT %s' % token['token'])

    def test_manager_permissions(self):
        pass

    def test_student_permissions(self):
        pass

    def test_anonymous_permissions(self):
        pass

# TODO: create tests for creaet Module and Page and check how change sort_index