from rest_framework import permissions

class IsSupervisor(permissions.BasePermission):
    """
    Permission check for supervisors.
    """

    def has_permission(self, request, view):
        current_user = request.user
        if current_user.role != 1:
            return False
        return True
