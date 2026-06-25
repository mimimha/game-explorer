from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    조회(GET 등 안전 메서드)는 누구나, 수정/삭제는 작성자만.
    작성자가 아니면 403.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user