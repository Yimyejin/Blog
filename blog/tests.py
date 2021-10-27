from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_james = User.objects.create_user(username='James', password='somepassword')
        self.user_trump = User.objects.create_user(username='Trump', password='somepassword')

    def navbar_test(self, soup):
        # 네비게이션바가 있다 - soup.nav로 soup에 담긴 내용 중 nav요소만 가져와 navbar에 저장한다.
        navbar = soup.nav
        # 네비게이션바에 Blog, AboutMe 라는 문구가 있다 - navbar의 텍스트 중에 Blog와 About me가 있는지 확인한다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo = navbar.find('a',text='Internet Programming')
        self.assertEqual(logo.attrs['href'], '/')
        home = navbar.find('a', text='Home')
        self.assertEqual(home.attrs['href'], '/')
        blog = navbar.find('a', text='Blog')
        self.assertEqual(blog.attrs['href'], '/blog/')
        about = navbar.find('a', text='About Me')
        self.assertEqual(about.attrs['href'], '/about_me/')

    def test_post_list(self):
        # 포스트 목록 페이지를 가져온다 - 127.0.0.1:8000/blog/를 입력했다고 가정하고 그때 열리는 웹 페이지 정보를 response 에 저장
        response = self.client.get('/blog/')
        # 정상적으로 페이지가 로드 - 404는 오류 200이 정상
        self.assertEqual(response.status_code, 200)
        # 페이지 타이틀이 'Blog' - 먼저 beautifulsoup으로 읽어들이고, html.parser 명령어로 파싱한 결과를 soup에 담는다. 그리고 title확인
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        self.navbar_test(soup)

        # 포스트(게시물)이 하나도 없는 경우 -
        self.assertEqual(Post.objects.count(),0)
        # 적절한 안내 문구가 포함되어 있는지 - id가 main-area인 div요소를 찾아 main_area에 저장한다. 그리고 Post레코드가 하나도 없으니 문구가 나타나느지 점검
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.',main_area.text)
        # 포스트(게시물)이 2개 존재하는 경우 - Post.objects.create()로 새로운 포스트를 만들 수 있음. 2개 만들고 2개인지 확인
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content = 'Hello World!!! We are the world...',
            author=self.user_james
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부가 아니잖아요',
            author=self.user_trump
        )
        self.assertEqual(Post.objects.count(),2)
        # 목록페이지를 새롭게 불러와서 - 새로고침하기 위해 1,3번째줄 일부 반복
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 포스트(게시물)의 타이틀이 2개 존재하는가 - 포스트가 생성되었으니 문구가 메인 영역에 더이상 없어야함 그래서 assertNotIn~
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)
        self.assertIn(self.user_james.username.upper(), main_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)
# post_list.html 에 본문영역에 해당하는 div 요소에 id="main-area"를 추가 -> {% if post_list.exists %} , {% else %] <h3>아직 게시물이~, {% endif %}

    def test_post_detail(self):
        # 포스트 하나 - 함수를 실행하면 새 데이터베이스를 만들고, 포스트를 하나 만든다.
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World!!! We are the world...',
            author = self.user_james
        )
        # 이 포스트의 url이 /blog/1 - 첫번째 포스트이므로 pk는 1 URL은 'blog/1/'이 된다.
        self.assertEqual(post_001.get_absolute_url(), '/blog/1')
        # url에 의해 정상적으로 상세페이지를 불러오는가 - '/blog/1'에 접근했을 때 status_code값이 200으로 반환되는지 확인하고, 파싱한다.
        response = self.client.get('/blog/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)

        # 포스트의 title은 웹브라우저의 title에 있는가 - 이 포스트의 title 필드 값이 웹 브라우저 탭의 타이틀에 있는지 확인한다.
        self.assertIn(post_001.title, soup.title.text)
        # 포스트의 title은 포스트영역에도 있는가 - id='main-area'인 div 요소를 찾고, 그 안에 di='post-area'인 div 요소를 찾아 post_area에 담는다.
        #                                    그리고 post_001 포스트의 title 필드 값이 포스트 영역 안에 있는지 확인한다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div',id="post-area")
        self.assertIn(post_001.title,post_area.text)
        # 포스트 작성자가 있는가 - 작성자가 화면에 보이는지 확인하는 내용이므로 현재는 개발할 수 없음
        # 아직 작성중
        # 포스트의 내용이 있는가 - 마지막으로 post_001의 내용이 포스트 영역에 있는지 확인한다.
        self.assertIn(post_001.content, post_area.text)

        self.assertIn(self.user_james.username.upper(), post_area.text)