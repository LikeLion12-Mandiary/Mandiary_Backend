from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from diarys.permissions import IsOwnerOrReadOnly
from .models import Todo
from .serializers import TodoSerializer
from rest_framework.response import Response
from rest_framework import status

class TodoListCreateAPIView(CreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

class TodoByDateAPIView(ListAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        selected_date = self.kwargs['selected_date']
        return Todo.objects.filter(user=self.request.user, date=selected_date)

    def get(self, request, selected_date):
        todos = self.get_queryset()
        serializer = self.get_serializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TodoListDestroyAPIView(DestroyAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'id'
    lookup_url_kwarg = 'todolist_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'삭제되었습니다.'},status=status.HTTP_204_NO_CONTENT)