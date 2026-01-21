from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post


class PostVisibilityAndAccessTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="123456"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="654321"
        )

        self.published_post1 = Post.objects.create(
            title = "Published Post of user1",
            content = "This is Published Post!",
            author = self.user1,
            is_published = True
        )
        self.unpublished_post1 = Post.objects.create(
            title = "Unpublished Post of user1",
            content = "This is Unpublished Post!",
            author = self.user1,
            is_published = False
        )
        self.published_post2 = Post.objects.create(
            title = "Published Post of user2",
            content = "This is Published Post!",
            author = self.user2,
            is_published = True
        )
        self.unpublished_post2 = Post.objects.create(
            title = "Unpublished Post of user2",
            content = "This is Unpublished Post!",
            author = self.user2,
            is_published = False
        )


    def get_detail_status(self, post:Post):
        url = reverse("post-detail", args=(post.id, ))
        response = self.client.get(url)
        return response.status_code


    def test_anonymous_user_sees_only_published_posts(self):
        """
        Anonymous users should only see published posts.
        """
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        ids = [post["id"] for post in response.data["results"]]
        self.assertIn(self.published_post1.id, ids)
        self.assertIn(self.published_post2.id, ids)
        self.assertNotIn(self.unpublished_post1.id, ids)
        self.assertNotIn(self.unpublished_post2.id, ids)


    def test_authenticated_user_sees_posts(self):
        """
        Authenticated users should only see published posts of others,
        and all of their posts.
        """
        logged_in = self.client.login(username="user1", password="123456")
        self.assertTrue(logged_in)
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        ids = [post["id"] for post in response.data["results"]]
        self.assertIn(self.published_post1.id, ids)
        self.assertIn(self.unpublished_post1.id, ids)
        self.assertIn(self.published_post2.id, ids)
        self.assertNotIn(self.unpublished_post2.id, ids)


    def test_anonymous_user_can_only_access_published_posts(self):
        """
        Anonymous users can only access published posts.
        """
        published_status = self.get_detail_status(self.published_post1)
        self.assertEqual(published_status, 200)

        unpublished_status = self.get_detail_status(self.unpublished_post1)
        self.assertEqual(unpublished_status, 404)


    def test_authenticated_user_can_access_posts(self):
        """
        Authenticated users can only access published posts of others,
        and all of their posts.
        """
        logged_in = self.client.login(username="user1", password="123456")
        self.assertTrue(logged_in)

        published_status1 = self.get_detail_status(self.published_post1)
        self.assertEqual(published_status1, 200)

        unpublished_status1 = self.get_detail_status(self.unpublished_post1)
        self.assertEqual(unpublished_status1, 200)

        published_status2 = self.get_detail_status(self.published_post2)
        self.assertEqual(published_status2, 200)

        unpublished_status2 = self.get_detail_status(self.unpublished_post2)
        self.assertEqual(unpublished_status2, 404)


class PostPermissionsTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="123456"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="654321"
        )

        self.post1 = Post.objects.create(
            title="Title",
            content="Content",
            author=self.user1,
            is_published=True
        )


    def test_anonymous_user_cannot_create_post(self):
        response = self.client.post(
            reverse("post-list"),
            data={"title":"title", "content": "content"}
        )

        self.assertEqual(response.status_code, 403)


    def test_authenticated_user_can_create_post(self):
        """
        Authenticated users can create posts,
        and the author is set to the requesting user.
        """
        logged_in = self.client.login(username="user1", password="123456")
        self.assertTrue(logged_in)

        response = self.client.post(
            reverse("post-list"),
            data={"title": "a title", "content": "a content"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["author"], "user1")


    def test_anonymous_user_cannot_update_post(self):
        url = reverse("post-detail", args=(self.post1.id, ))
        response = self.client.patch(
            url, data={"title": "changed title"}
        )
        self.assertEqual(response.status_code, 403)


    def test_anonymous_user_cannot_delete_post(self):
        url = reverse("post-detail", args=(self.post1.id, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)


    def test_authenticated_user_cannot_update_others_post(self):
        logged_in = self.client.login(username="user2", password="654321")
        self.assertTrue(logged_in)

        url = reverse("post-detail", args=(self.post1.id, ))
        response = self.client.patch(
            url, data={"title": "changed title"}
        )
        self.assertEqual(response.status_code, 403)


    def test_authenticated_user_cannot_delete_others_post(self):
        logged_in = self.client.login(username="user2", password="654321")
        self.assertTrue(logged_in)

        url = reverse("post-detail", args=(self.post1.id, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)


    def test_authenticated_user_can_update_their_post(self):
        logged_in = self.client.login(username="user1", password="123456")
        self.assertTrue(logged_in)

        url = reverse("post-detail", args=(self.post1.id, ))
        response = self.client.patch(
            url, data={"title": "changed title"}
        )
        self.assertEqual(response.status_code, 200)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "changed title")


    def test_authenticated_user_can_delete_their_post(self):
        logged_in = self.client.login(username="user1", password="123456")
        self.assertTrue(logged_in)

        url = reverse("post-detail", args=(self.post1.id, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Post.objects.filter(id=self.post1.id).exists())
