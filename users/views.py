from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .permissions import IsOwnerOrReadOnly
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

#로그인
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'잘못된 이메일 혹은 비밀번호입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.password):
            return Response({'잘못된 이메일 혹은 비밀번호입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        token = RefreshToken.for_user(user)
        serializer = UserSerializer(user)
        return Response(
            status=status.HTTP_200_OK,
            data={
                'token': str(token.access_token),
                'user': serializer.data,
            }
        )
    
# 회원가입
class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

#이메일 중복 확인
class UserEmailCheckAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({'이미 사용중인 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'사용 가능한 이메일입니다.'}, status=status.HTTP_200_OK)
# 마이프로필
class ProfileAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    def get_object(self):
        return self.request.user

#이메일 전송
class EmailConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            code = get_random_string(length=6, allowed_chars='0123456789')
            user.reset_code = code
            user.save()
            send_mail(
                'Your Password Reset Code',
                f'Use this code to reset your password: {code}',
                'tjgustjr16@naver.com',
                [email],
            )
            return Response({'인증코드를 보냈습니다.'}, status=status.HTTP_200_OK)
        return Response({'존재하지 않는 이메일 입니다.'}, status=status.HTTP_404_NOT_FOUND)

#비밀번호 재설정
class PasswordChangeAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        confirm_code = request.data.get('confirm_code')
        new_password = request.data.get('new_password')
        user = User.objects.filter(email=email).first()
        if user and user.reset_code == confirm_code:
            user.set_password(new_password)
            user.reset_code = ''
            user.save()
            return Response({'비밀번호를 재설정 했습니다.'}, status=status.HTTP_200_OK)
        return Response({'올바르지 않은 이메일 혹은 인증번호입니다.'}, status=status.HTTP_400_BAD_REQUEST)