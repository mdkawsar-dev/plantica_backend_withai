from django.urls import path
from .views import (
    CommunityPostListView,
    CommunityPostDetailView,
    PostLikeToggleView,
    AddCommentView,
    AddReplyCommentView,
    CommunityHighlightView
)

urlpatterns = [
    # 1. Feed (GET) & New Post Create (POST)
    path('posts/', CommunityPostListView.as_view(), name='post_list_create'),
    
    # 2. Community Highlights (Top 3 Engagement Posts)
    path('posts/highlights/', CommunityHighlightView.as_view(), name='community_highlights'),
    
    # 3. Post Detail (GET)
    path('posts/<int:pk>/', CommunityPostDetailView.as_view(), name='post_detail'),
    
    # 4. Post Like / Unlike Toggle (POST)
    path('posts/<int:pk>/like/', PostLikeToggleView.as_view(), name='post_like_toggle'),
    
    # 5. Main Comment Create (POST)
    path('posts/<int:pk>/comments/', AddCommentView.as_view(), name='add_comment'),
    
    # 6. Comment Reply Create (POST)
    path('comments/<int:comment_id>/reply/', AddReplyCommentView.as_view(), name='add_reply'),
]
