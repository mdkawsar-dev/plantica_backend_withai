from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status, viewsets
from django.db.models import Q
from plantica_core.responses import custom_response, success_response, error_response
from .models import MarketplaceListing
from .serializers import MarketplaceListingSerializer

# --- 1. Feed, Search, Filter (GET) & Create Listing (POST) ---
class MarketplaceProductListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        queryset = MarketplaceListing.objects.filter(is_sold=False).order_by('-created_at')

        # Search filter (title, description, location)
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        # Category filter (বীজ, চারাগাছ, টব, সার, টুলস)
        category_query = request.query_params.get('category', None)
        if category_query and category_query != 'সব':
            queryset = queryset.filter(category=category_query)

        serializer = MarketplaceListingSerializer(queryset, many=True, context={'request': request})
        
        return custom_response(
            data=serializer.data,
            message="মার্কেটপ্লেসের পণ্যসমূহ সফলভাবে পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )

    def post(self, request):
        serializer = MarketplaceListingSerializer(data=request.data)
        if serializer.is_valid():
            user_location = getattr(request.user.profile, 'address', 'ঢাকা') if hasattr(request.user, 'profile') and request.user.profile.address else 'ঢাকা'
            location_val = request.data.get('location') or user_location
            serializer.save(seller=request.user, location=location_val)
            
            return custom_response(
                data=serializer.data,
                message="আপনার লিস্টিংটি সফলভাবে তৈরি করা হয়েছে!",
                code=status.HTTP_201_CREATED,
                status=True
            )

        return custom_response(
            data=serializer.errors,
            message="লিস্টিং তৈরি করতে ব্যর্থ হয়েছে",
            code=status.HTTP_400_BAD_REQUEST,
            status=False
        )


# --- 2. My Listings API (GET) ---
class MyListingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        my_products = MarketplaceListing.objects.filter(seller=request.user).order_by('-created_at')
        serializer = MarketplaceListingSerializer(my_products, many=True, context={'request': request})

        return custom_response(
            data=serializer.data,
            message="আপনার লিস্টিং তালিকা সফলভাবে আনা হয়েছে",
            code=status.HTTP_200_OK,
            status=True
        )


# --- 3. Edit (PUT/PATCH) & Delete (DELETE) API ---
class MarketplaceProductDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return MarketplaceListing.objects.get(pk=pk)
        except MarketplaceListing.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return custom_response(
                data=None,
                message="পণ্যটি পাওয়া যায়নি।",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )
        serializer = MarketplaceListingSerializer(product, context={'request': request})
        return custom_response(
            data=serializer.data,
            message="পণ্যের বিস্তারিত তথ্য পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )

    def put(self, request, pk):
        return self.update_product(request, pk, partial=False)

    def patch(self, request, pk):
        return self.update_product(request, pk, partial=True)

    def update_product(self, request, pk, partial=False):
        product = self.get_object(pk)
        if not product or product.seller != request.user:
            return custom_response(
                data=None,
                message="পণ্যটি পাওয়া যায়নি অথবা আপনার এটি সম্পাদনা করার অনুমতি নেই।",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )

        serializer = MarketplaceListingSerializer(product, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return custom_response(
                data=serializer.data,
                message="লিস্টিংটি সফলভাবে সম্পাদন করা হয়েছে",
                code=status.HTTP_200_OK,
                status=True
            )

        return custom_response(
            data=serializer.errors,
            message="সম্পাদনা ব্যর্থ হয়েছে",
            code=status.HTTP_400_BAD_REQUEST,
            status=False
        )

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product or product.seller != request.user:
            return custom_response(
                data=None,
                message="পণ্যটি পাওয়া যায়নি অথবা এটি মোছার অনুমতি নেই।",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )

        product.delete()
        return custom_response(
            data=None,
            message="লিস্টিংটি মুছে ফেলা হয়েছে",
            code=status.HTTP_200_OK,
            status=True
        )


# --- 4. Mark Stockout Toggle API (PATCH) ---
class MarkStockoutView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            product = MarketplaceListing.objects.get(pk=pk, seller=request.user)
            product.is_sold = not product.is_sold
            product.save()

            status_msg = "পণ্যটি 'বিক্রি হয়েছে' হিসেবে চিহ্নিত করা হলো" if product.is_sold else "পণ্যটি পুনরায় বিক্রির জন্য সক্রিয় করা হলো"

            return custom_response(
                data={"id": product.id, "is_sold": product.is_sold},
                message=status_msg,
                code=status.HTTP_200_OK,
                status=True
            )
        except MarketplaceListing.DoesNotExist:
            return custom_response(
                data=None,
                message="পণ্যটি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


class MarketplaceListingViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceListing.objects.all().order_by('-created_at')
    serializer_class = MarketplaceListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
