from diarys.models import Diary
from diarys.serializers import DiarySerializer
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from diarys.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
import os
from rest_framework import status

# 다이어리 생성
class DiaryCreateAPIView(CreateAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 유저 전체 다이어리 조회
class UserDiarysAPIView(ListAPIView):
    serializer_class = DiarySerializer
    
    def get_queryset(self):
        return self.request.user.diarys.all()
    
# 게시글 확인, 수정, 삭제
class DiaryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'id'
    lookup_url_kwarg = 'diary_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"게시글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        if instance.image:
            image_path = instance.image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
        instance.delete()

    def perform_update(self, serializer):
        instance = serializer.instance
        
        # 기존 이미지가 제거되는 경우
        if 'image' in self.request.data and not self.request.data['image']:
            if instance.image:
                image_path = instance.image.path
                if os.path.isfile(image_path):
                    os.remove(image_path)
        serializer.save()
