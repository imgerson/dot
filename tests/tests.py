#! /usr/bin/env python

import unittest
import os

from dot import Dot
from dot import Post
from dot import Flatpage


class TestDot(unittest.TestCase):

    def setUp(self):
        self.blog = Dot()
        self.blog.generate()

    def tearDown(self):
        self.blog.remove_all()

    def test_create_markdown_blog_post(self):
        blog_post_title = 'Some Blog Post Title in Here'

        markdown_created, _ = self.blog.create_blog_post(blog_post_title)

        self.assertTrue(markdown_created)

    def test_create_duplicate_markdown_blog_post(self):
        blog_post_title = 'Title to Be Repeated'

        markdown_created, _ = self.blog.create_blog_post(blog_post_title)

        self.assertTrue(markdown_created)
        self.assertRaises(EnvironmentError, self.blog.create_blog_post,
            blog_post_title)

    def test_create_markdown_flatpage(self):
        flatpage_title = 'Home'

        flatpage_created, _ = self.blog.create_flatpage(flatpage_title)

        self.assertTrue(flatpage_created)

    def test_create_duplicate_markdown_flatpage(self):
        flatpage_title = 'Home'

        flatpage_created, _ = self.blog.create_flatpage(flatpage_title)

        self.assertTrue(flatpage_created)
        self.assertRaises(EnvironmentError, self.blog.create_flatpage,
            flatpage_title)

    def test_publication_of_blog_post(self):
        blog_post_title = 'Dot'

        _, blog_post = self.blog.create_blog_post(blog_post_title)

        self.assertTrue(self.blog.generate())

        blog_published = os.path.join(self.blog.output_dir, self.blog.blog_dir,
            blog_post, 'index.html')

        self.assertTrue(os.path.exists(blog_published))

    def test_publication_of_flatpage(self):
        flatpage_title = 'Dot'

        _, blog_flatpage = self.blog.create_flatpage(flatpage_title)

        self.assertTrue(self.blog.generate())

        flatpage_published = os.path.join(self.blog.output_dir,
            self.blog.flatpage_dir, blog_flatpage, 'index.html')

        self.assertTrue(os.path.exists(flatpage_published))


if __name__ == '__main__':
    unittest.main()
