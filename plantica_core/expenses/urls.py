from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseSummaryView, AddExpenseView, GardeningExpenseViewSet

router = DefaultRouter()
router.register(r'gardening-expenses', GardeningExpenseViewSet, basename='gardening-expense')

urlpatterns = [
    path('summary/', ExpenseSummaryView.as_view(), name='expense_summary'),
    path('add/', AddExpenseView.as_view(), name='add_expense'),
    path('', include(router.urls)),
]
