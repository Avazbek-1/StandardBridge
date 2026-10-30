from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return '/dashboard/'


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Google orqali kirgan foydalanuvchini tizimga ulash yoki yangi yaratish."""
        # Agar email bo'yicha mavjud foydalanuvchi topilsa — uning hisobiyla kir
        if sociallogin.is_existing:
            return
        email = sociallogin.account.extra_data.get('email', '')
        if not email:
            return
        from accounts.models import CustomUser
        try:
            existing = CustomUser.objects.get(email__iexact=email)
            sociallogin.connect(request, existing)
        except CustomUser.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """Yangi Google foydalanuvchisi uchun CustomUser va uning profilini xavfsiz yaratish."""
        data = sociallogin.account.extra_data
        email = data.get('email', '')
        first_name = data.get('given_name') or data.get('first_name', '')
        last_name = data.get('family_name') or data.get('last_name', '')
        
        from accounts.models import CustomUser, ExpertProfile, EntrepreneurProfile
        import re

        if email:
            existing_user = CustomUser.objects.filter(email__iexact=email).first()
            if existing_user:
                return existing_user

        # Unique username generatsiya qilish
        base = re.sub(r'[^a-zA-Z0-9_]', '', email.split('@')[0])[:15] or 'user'
        username = base
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f'{base}{counter}'
            counter += 1

        # Rolni session yoki cookie dan o'qish, default 'entrepreneur'
        role = request.session.get('signup_role') or request.COOKIES.get('signup_role', 'entrepreneur')
        if role not in ['entrepreneur', 'expert']:
            role = 'entrepreneur'

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_email_verified=True,
        )

        if role == 'expert':
            ExpertProfile.objects.get_or_create(user=user)
        else:
            EntrepreneurProfile.objects.get_or_create(user=user)

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return '/dashboard/'
