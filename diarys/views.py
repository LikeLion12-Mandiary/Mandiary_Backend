from diarys.models import Diary
from diarys.serializers import DiarySerializer
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from diarys.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
import os
from rest_framework import status

#게시글 전체 확인, 게시글 생성
class DiaryListCreateAPIView(ListCreateAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
#게시글 확인, 수정, 삭제
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
        if 'image' in serializer.validated_data and not serializer.validated_data['image']:
            if instance.image:
                image_path = instance.image.path
                if os.path.isfile(image_path):
                    os.remove(image_path)
            instance.image = None

        # 데이터베이스에 변경 사항 저장
        serializer.save()