from django.shortcuts import render

from blog.models import Comment, Post
from user.models import User

from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='login')    
def blog(request):
    posts = Post.objects.select_related('author')
    user = User.objects.get(id=request.user.id)
    comments = Comment.objects.all()
    if request.POST.get('post') == 'post':
        description = request.POST.get('input')
        Post.objects.create(description=description,
                            author = user)
    if request.POST.get('comment') == 'comment':
        comment = request.POST.get('message')
        post_id = request.POST.get('post_id')
        cur_post = Post.objects.get(post_id=post_id)
        Comment.objects.create(body=comment, post=cur_post, user=request.user)
        
   
        

    context = {'posts':posts, 'comments':comments}

    return render(request, 'blog/blog.html', context)
