from app.shared.base_permission import PermissionsBase


class PermissionPermission(PermissionsBase, prefix='permission'):
    CAN_VIEW_PERMISSION = "can_view"
    CAN_ADD_PERMISSION = "can_add"
    CAN_EDIT_PERMISSION = "can_edit"
    CAN_DELETE_PERMISSION = "can_delete"
    CAN_LIST_PERMISSIONS = "can_list"
