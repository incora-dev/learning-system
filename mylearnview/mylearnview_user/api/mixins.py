from .permissions import IsManagerPermission


class ManagerPermissionCreateUpdate:
    # For post, put, patch set only manager permission

    def get_permissions(self):
        if self.request.method == 'GET':
            return super().get_permissions()
        else:
            return super().get_permissions() + [IsManagerPermission()]