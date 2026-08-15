from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CommunityPost, PostImage, PostLike, PostComment

User = get_user_model()

# Author info serializer
class AuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'profile') and obj.profile.avatar:
            if request:
                return request.build_absolute_uri(obj.profile.avatar.url)
            return obj.profile.avatar.url
        return None


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']


# --- Reply Comment Serializer ---
class CommentReplySerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'comment_text', 'created_at']


# --- Main Comment (with nested replies thread) ---
class PostCommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'comment_text', 'created_at', 'replies']


# --- Post List (Feed View) ---
class CommunityPostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source='user', read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = ['id', 'author', 'category', 'text_content', 'images', 'likes_count', 'comments_count', 'is_liked', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


# --- Post Detail (with liked users & comments thread) ---
class CommunityPostDetailSerializer(CommunityPostListSerializer):
    liked_by_users = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta(CommunityPostListSerializer.Meta):
        fields = CommunityPostListSerializer.Meta.fields + ['liked_by_users', 'comments']

    def get_liked_by_users(self, obj):
        likes = obj.likes.select_related('user').order_by('-created_at')[:5]
        return [AuthorSerializer(like.user, context=self.context).data for like in likes]

    def get_comments(self, obj):
        main_comments = obj.comments.filter(parent__isnull=True).order_by('-created_at')
        return PostCommentSerializer(main_comments, many=True, context=self.context).data
