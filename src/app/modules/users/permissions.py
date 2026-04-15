from app.shared.base_permission import PermissionsBase


class UserPermission(PermissionsBase, prefix='user'):
    CAN_EDIT_USER = "can_edit"
    CAN_ADD_USER = "can_add"
    CAN_DELETE_USER = "can_delete"
    CAN_VIEW_USER = "can_view"
    CAN_LIST_USERS = "can_list"


