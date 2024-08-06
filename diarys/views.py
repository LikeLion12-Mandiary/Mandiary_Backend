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
    
    def perform_destroy(self, instance):
        # image1과 image2가 존재할 경우 파일 삭제
        if instance.image1:
            image1_path = instance.image1.path
            if os.path.isfile(image1_path):
                os.remove(image1_path)
        
        if instance.image2:
            image2_path = instance.image2.path
            if os.path.isfile(image2_path):
                os.remove(image2_path)

        instance.delete()

    def perform_update(self, serializer):
        instance = serializer.instance
        
        # 기존 이미지가 제거되는 경우
        if 'image1' in self.request.data and not self.request.data['image1']:
            if instance.image1:
                image1_path = instance.image1.path
                if os.path.isfile(image1_path):
                    os.remove(image1_path)

        if 'image2' in self.request.data and not self.request.data['image2']:
            if instance.image2:
                image2_path = instance.image2.path
                if os.path.isfile(image2_path):
                    os.remove(image2_path)

        serializer.save()
