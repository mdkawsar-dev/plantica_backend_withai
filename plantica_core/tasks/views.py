from rest_framework import viewsets, permissions, status
from plantica_core.responses import success_response, error_response
from .models import GardeningTask
from .serializers import GardeningTaskSerializer

class GardeningTaskViewSet(viewsets.ModelViewSet):
    serializer_class = GardeningTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GardeningTask.objects.filter(user=self.request.user).order_by('scheduled_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Gardening tasks fetched successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(data=serializer.data, message="Task created successfully", code=status.HTTP_201_CREATED)
        return error_response(message="Failed to create task", data=serializer.errors)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Task details retrieved successfully")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="Task updated successfully")
        return error_response(message="Failed to update task", data=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="Task deleted successfully", code=status.HTTP_204_NO_CONTENT)
