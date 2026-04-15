from app.shared.base_permission import PermissionsBase


class GroupPermission(PermissionsBase, prefix='group'):
    CAN_EDIT_GROUP = "can_edit"
    CAN_ADD_GROUP = "can_add"
    CAN_DELETE_GROUP = "can_delete"
    CAN_VIEW_GROUP = "can_view"
    CAN_LIST_GROUPS = "can_list"
    CAN_MANAGE_GROUP_USERS = "can_manage_group_users"
    CAN_MANAGE_GROUP_PERMISSIONS = "can_manage_group_permissions"
