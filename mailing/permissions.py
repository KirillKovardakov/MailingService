from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    """Базовый миксин для проверки роли пользователя."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role not in self.allowed_roles:
            raise PermissionDenied("Недостаточно прав для выполнения этого действия.")
        if profile.is_blocked:
            raise PermissionDenied("Ваш аккаунт заблокирован администратором.")
        return super().dispatch(request, *args, **kwargs)


class ManagerOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['manager']


class UserOrManagerMixin(RoleRequiredMixin):
    allowed_roles = ['user', 'manager']
