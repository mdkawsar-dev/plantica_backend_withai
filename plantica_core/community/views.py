from django.db.models import Count, F
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from plantica_core.responses import custom_response, success_response, error_response
from .models import CommunityPost, PostImage, PostLike, PostComment
from .serializers import (
    CommunityPostListSerializer, 
    CommunityPostDetailSerializer, 
    PostCommentSerializer
)

# --- 1. Feed (GET) & New Post Create (POST) ---
class CommunityPostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        queryset = CommunityPost.objects.all().order_by('-created_at')

        # Category filter (সব, প্রশ্ন, টিপস, গাছের ছবি)
        category = request.query_params.get('category', None)
        if category and category != 'সব':
            queryset = queryset.filter(category=category)

        serializer = CommunityPostListSerializer(queryset, many=True, context={'request': request})
        return custom_response(
            data=serializer.data,
            message="কমিউনিটি পোস্টসমূহ সফলভাবে আনা হয়েছে",
            code=status.HTTP_200_OK,
            status=True
        )

    def post(self, request):
        category = request.data.get('category')
        text_content = request.data.get('text_content')

        if not category or not text_content:
            return custom_response(
                data=None,
                message="ক্যাটাগরি এবং পোস্টের বিবরণ দেয়া আবশ্যক।",
                code=status.HTTP_400_BAD_REQUEST,
                status=False
            )

        post_obj = CommunityPost.objects.create(
            user=request.user,
            category=category,
            text_content=text_content
        )

        # Multi-Image Upload
        images = request.FILES.getlist('images')
        for img in images:
            PostImage.objects.create(post=post_obj, image=img)

        serializer = CommunityPostDetailSerializer(post_obj, context={'request': request})
        return custom_response(
            data=serializer.data,
            message="আপনার পোস্টটি সফলভাবে পাবলিশ করা হয়েছে!",
            code=status.HTTP_201_CREATED,
            status=True
        )


# --- 2. Post Detail API (GET) ---
class CommunityPostDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            post_obj = CommunityPost.objects.get(pk=pk)
            serializer = CommunityPostDetailSerializer(post_obj, context={'request': request})
            return custom_response(
                data=serializer.data,
                message="পোস্টের বিস্তারিত পাওয়া গেছে",
                code=status.HTTP_200_OK,
                status=True
            )
        except CommunityPost.DoesNotExist:
            return custom_response(
                data=None,
                message="পোস্টটি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


# --- 3. Like / Unlike Toggle API (POST) ---
class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post_obj = CommunityPost.objects.get(pk=pk)
            like_obj, created = PostLike.objects.get_or_create(post=post_obj, user=request.user)

            if not created:
                like_obj.delete()
                is_liked = False
                msg = "লাইক মুছে ফেলা হয়েছে"
            else:
                is_liked = True
                msg = "পোস্টে লাইক দেওয়া হয়েছে"

            return custom_response(
                data={"post_id": pk, "is_liked": is_liked, "total_likes": post_obj.likes.count()},
                message=msg,
                code=status.HTTP_200_OK,
                status=True
            )
        except CommunityPost.DoesNotExist:
            return custom_response(
                data=None,
                message="পোস্টটি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


# --- 4. Main Comment API (POST) ---
class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        comment_text = request.data.get('comment_text')
        if not comment_text:
            return custom_response(
                data=None,
                message="কমেন্টের লেখা দেয়া আবশ্যক।",
                code=status.HTTP_400_BAD_REQUEST,
                status=False
            )

        try:
            post_obj = CommunityPost.objects.get(pk=pk)
            comment = PostComment.objects.create(
                post=post_obj,
                user=request.user,
                comment_text=comment_text
            )
            serializer = PostCommentSerializer(comment, context={'request': request})
            return custom_response(
                data=serializer.data,
                message="কমেন্ট যুক্ত করা হয়েছে",
                code=status.HTTP_201_CREATED,
                status=True
            )
        except CommunityPost.DoesNotExist:
            return custom_response(
                data=None,
                message="পোস্টটি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


# --- 5. Comment Reply API (POST) ---
class AddReplyCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        comment_text = request.data.get('comment_text')
        if not comment_text:
            return custom_response(
                data=None,
                message="উত্তরের লেখা দেয়া আবশ্যক।",
                code=status.HTTP_400_BAD_REQUEST,
                status=False
            )

        try:
            parent_comment = PostComment.objects.get(pk=comment_id)
            reply = PostComment.objects.create(
                post=parent_comment.post,
                user=request.user,
                parent=parent_comment,
                comment_text=comment_text
            )
            serializer = PostCommentSerializer(parent_comment, context={'request': request})
            return custom_response(
                data=serializer.data,
                message="উত্তর যুক্ত করা হয়েছে",
                code=status.HTTP_201_CREATED,
                status=True
            )
        except PostComment.DoesNotExist:
            return custom_response(
                data=None,
                message="মূল কমেন্টটি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


# --- 6. Community Highlight API (Top 3 Engagement Posts) ---
class CommunityHighlightView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        top_posts = CommunityPost.objects.annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
            engagement=F('like_count') + F('comment_count')
        ).order_by('-engagement', '-created_at')[:3]

        serializer = CommunityPostListSerializer(top_posts, many=True, context={'request': request})
        return custom_response(
            data=serializer.data,
            message="কমিউনিটি হাইলাইট পোস্টসমূহ পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )
