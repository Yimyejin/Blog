from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        # 포스트 목록 페이지를 가져온다
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀이 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        # 네비게이션바가 있다
        navbar = soup.nav
        # 네비게이션바에 Blog, AboutMe 라는 문구가 있다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 포스트(게시물)이 하나도 없는 경우
        self.assertEqual(Post.objects.count(),0)
        # 적절한 안내 문구가 포함되어 있는지
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.',main_area.text)
        # 포스트(게시물)이 2개 존재하는 경우
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content = 'Hello World!!! We are the world...'
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부가 아니잖아요'
        )
        self.assertEqual(Post.objects.count(),2)
        # 목록페이지를 새롭게 불러와서
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 포스트(게시물)의 타이틀이 2개 존재하는가
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)


    def test_post_detail(self):
        # 포스트 하나
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World!!! We are the world...'
        )
        # 이 포스트의 url이 /blog/1
        self.assertEqual(post_001.get_absolute_url(), '/blog/1')
        # url에 의해 정상적으로 상세페이지를 불러오는가
        response = self.client.get('/blog/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 포스트목록과 같은 네비게이션바가 있는가
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)
        # 포스트의 title은 웹브라우저의 title에 있는가
        self.assertIn(post_001.title, soup.title.text)
        # 포스트의 title은 포스트영역에도 있는가
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div',id="post-area")
        self.assertIn(post_001.title,post_area.text)
        # 포스트 작성자가 있는가
        # 아직 작성중
        # 포스트의 내용이 있는가
        self.assertIn(post_001.content, post_area.text)