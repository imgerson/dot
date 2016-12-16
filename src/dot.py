#! /usr/bin/env python

from jinja2 import Environment, FileSystemLoader

import markdown2

import shutil
import os
import re
import sys
import glob
import argparse
import datetime


class Dot():
    content_dir = 'content'
    output_dir = 'html'
    blog_dir = 'blog'
    flatpage_dir = ''
    templates_dir = 'templates'
    template_environment = None

    def _get_template_env(self):
        self.template_environment = Environment(
            loader=FileSystemLoader(self.templates_dir))

    def clean_output_dir(self):
        try:
            shutil.rmtree(self.output_dir)
        except OSError:
            pass

    def remove_all(self):
        try:
            shutil.rmtree(self.output_dir)
            shutil.rmtree(self.content_dir)
        except OSError:
            pass

    def generate_structure(self):
        common_dirs = '{static,media}'
        cmd = 'mkdir -p {content_dir}/{common_dirs} templates'

        os.system(cmd.format(
            content_dir=self.content_dir, common_dirs=common_dirs))

        if self.blog_dir:
            blog_dir = os.path.join(self.content_dir, self.blog_dir)
            cmd = 'mkdir -p {blog_dir}/{common_dirs}'.format(
                blog_dir=blog_dir, common_dirs=common_dirs)
            os.system(cmd)

        if self.flatpage_dir:
            flatpage_dir = os.path.join(self.content_dir, self.flatpage_dir)
            cmd = 'mkdir -p {flatpage_dir}/{common_dirs}'.format(
                flatpage_dir=flatpage_dir, common_dirs=common_dirs)
            os.system(cmd)

        shutil.copytree(
            self.content_dir, self.output_dir,
            ignore=shutil.ignore_patterns('*.md'))

    @property
    def posts(self):
        path = os.path.join(self.content_dir, self.blog_dir)

        return glob.glob(os.path.join(path, '*.md'))

    @property
    def flatpages(self):
        path = os.path.join(self.content_dir, self.flatpage_dir)

        return glob.glob(os.path.join(path, '*.md'))

    def create_blog_post(self, title):
        today = datetime.date.today()
        new_post = Post()
        new_post.load(title=title, date=today)

        mdcontent = new_post.get_markdown_content()

        path_to_md = os.path.join(self.content_dir, self.blog_dir,
            '{}.md'.format(new_post.filename))

        if os.path.isfile(path_to_md):
            raise EnvironmentError('File already exists')

        with open(path_to_md, 'w') as md:
            md.write(mdcontent)

        return (True, new_post.filename)

    def create_flatpage(self, title):
        today = datetime.date.today()
        new_flatpage = Flatpage()
        new_flatpage.load(title=title, date=today)

        mdcontent = new_flatpage.get_markdown_content()

        path_to_md = os.path.join(self.content_dir, self.flatpage_dir,
            '{}.md'.format(new_flatpage.filename))

        if os.path.exists(path_to_md):
            raise EnvironmentError('File already exists')

        with open(path_to_md, 'w') as md:
            md.write(mdcontent)

        return (True, new_flatpage.filename)

    def generate_flatpages(self):
        if not self.template_environment:
            self._get_template_env()

        index_template = self.template_environment.get_template('index.html')
        flatpages_template = self.template_environment.get_template(
            'flatpage.html')

        index_html = index_template.render()
        path_to_index = os.path.join(self.output_dir, self.flatpage_dir,
            'index.html')

        with open(path_to_index, 'w') as index:
            index.write(index_html)

        for flatpage in self.flatpages:
            new_flatpage = Flatpage()
            new_flatpage.load(path_to_md=flatpage)

            html = flatpages_template.render(flatpage=new_flatpage)

            path = os.path.join(self.output_dir, self.flatpage_dir,
                new_flatpage.filename)

            if not os.path.exists(path):
                os.makedirs(path)

            path_to_file = os.path.join(path, 'index.html')

            with open(path_to_file, 'w') as post:
                post.write(html)

    def generate_posts(self):
        if not self.template_environment:
            self._get_template_env()

        index_template = self.template_environment.get_template(
            'blogindex.html')
        post_template = self.template_environment.get_template('post.html')

        index_html = index_template.render(posts=self.posts)
        path_to_index = os.path.join(self.output_dir, self.blog_dir,
            'index.html')

        with open(path_to_index, 'w') as index:
            index.write(index_html)

        for post in self.posts:
            new_post = Post()
            new_post.load(path_to_md=post)

            html = post_template.render(post=new_post)

            path = os.path.join(self.output_dir, self.blog_dir,
                new_post.filename)

            if not os.path.exists(path):
                os.makedirs(path)

            path_to_file = os.path.join(path, 'index.html')

            with open(path_to_file, 'w') as output_post:
                output_post.write(html)

    def generate(self):
        self.clean_output_dir()
        self.generate_structure()
        self.generate_flatpages()
        self.generate_posts()

        return True


class Page():
    title = None
    date = None
    html = None
    mdcontent = None
    filename = None

    def slugify(self, value):
        return re.sub('[^\w]+', '-', value.strip().lower())

    @property
    def filename(self):
        return self.slugify(self.title)

    def get_markdown_content(self):
        if not self.mdcontent:
            markdown_template = """---\ntitle:{title}\ndate:{date}\n---"""

            self.mdcontent = markdown_template.format(title=self.title,
                date=self.date)

        return self.mdcontent

    def load(self, path_to_md=False, **args):
        try:
            self.title = args['title']
            self.date = args['date']

            return True
        except KeyError:
            pass

        with open(path_to_md) as md:
            self.mdcontent = md.read()

        self.html = markdown2.markdown(self.mdcontent, extras=['metadata'])

        self.title = self.html.metadata['title']
        self.date = self.html.metadata['date']

        return True

class Post(Page):

    @property
    def filename(self):
        today = datetime.date.today()
        slug = '{date}--{slug}'.format(
            date=today, slug=self.slugify(self.title))

        return slug


class Flatpage(Page):
    pass


def main():
    blog = Dot()

    parser = argparse.ArgumentParser(prog='DOT')

    subparsers = parser.add_subparsers()

    parser_generate = subparsers.add_parser('generate', help='Generate site')
    parser_generate.set_defaults(func=blog.generate())

    parser_new = subparsers.add_parser('new', help='Generatemarkdown file')
    parser_new.add_argument('--post')
    parser_new.add_argument('--flatpage')

    args = parser.parse_args()

    try:
        blog.create_blog_post(args.post)
    except AttributeError:
        pass

    try:
        blog.create_flatpage(args.flatpage)
    except AttributeError:
        pass


if __name__ == '__main__':
    sys.exit(main())
