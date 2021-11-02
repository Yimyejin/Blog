# 아래 문장은 render 임포트할때만 사용하므로 CBV로 바꿀때 삭제해도됨. DetailView도 CBV로 바꿀때 추가
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Post, Category


# Create your views here.
class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


#    template_name = 'blog/post_list.html'
# 파일명 post_list.html 으로 수정

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


#    template_name = 'blog/post_detail.html'
# post_detail.html 으로 이름 수정

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(request, 'blog/post_list.html',
                  {
                      'post_list': post_list,
                      'categories': Category.objects.all(),
                      'no_category_post_count': Post.objects.filter(category=None).count(),
                      'category': category
                  }
                  )

# FBV로 만들기
# def index(request):
#    posts = Post.objects.all().order_by('-pk')
#
#    return render(request, 'blog/post_list.html',
#                  {
#                      'posts': posts
#                  }
#                  )
# 원래는 for p in posts -> CBV에서는 for p in post_list
# 상세페이지
# def single_post_page(request, pk):
#    post = Post.objects.get(pk=pk)
#
#    return render(request, 'blog/post_detail.html',
#                  {
#                      'post': post
#                  }
#                  )
