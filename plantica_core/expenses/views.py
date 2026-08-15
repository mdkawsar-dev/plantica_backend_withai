from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.db.models import Sum
from django.utils import timezone
from plantica_core.responses import custom_response, success_response, error_response
from .models import GardeningExpense
from .serializers import GardeningExpenseSerializer

# --- 1. Expense Summary & History API (GET) ---
class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # Total expenses for current month
        monthly_expenses = GardeningExpense.objects.filter(
            user=user,
            date__year=now.year,
            date__month=now.month
        )
        total_monthly_amount = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Pie chart category breakdown
        category_breakdown = []
        categories = ['গাছ', 'সার', 'টব', 'অন্যান্য']
        
        all_time_total = GardeningExpense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

        for cat in categories:
            cat_sum = GardeningExpense.objects.filter(user=user, category=cat).aggregate(total=Sum('amount'))['total'] or 0
            percentage = round((cat_sum / all_time_total) * 100) if all_time_total > 0 else 0
            category_breakdown.append({
                "category": cat,
                "amount": float(cat_sum),
                "percentage": percentage
            })

        # Recent expenses history (last 10)
        recent_expenses = GardeningExpense.objects.filter(user=user).order_by('-date', '-id')[:10]
        serializer = GardeningExpenseSerializer(recent_expenses, many=True, context={'request': request})

        data = {
            "current_month_total": float(total_monthly_amount),
            "category_breakdown": category_breakdown,
            "recent_expenses": serializer.data
        }

        return custom_response(
            data=data,
            message="খরচের হিসাব সফলভাবে তুলে আনা হয়েছে",
            code=status.HTTP_200_OK,
            status=True
        )


# --- 2. Add Expense API (POST) ---
class AddExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GardeningExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return custom_response(
                data=serializer.data,
                message="নতুন খরচ সফলভাবে সংরক্ষণ করা হয়েছে",
                code=status.HTTP_201_CREATED,
                status=True
            )
            
        return custom_response(
            data=serializer.errors,
            message="খরচ যোগ করতে ব্যর্থ হয়েছে",
            code=status.HTTP_400_BAD_REQUEST,
            status=False
        )


class GardeningExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = GardeningExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GardeningExpense.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Expenses fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(data=serializer.data, message="Expense recorded successfully", code=status.HTTP_201_CREATED)
        return error_response(message="Failed to record expense", data=serializer.errors)
