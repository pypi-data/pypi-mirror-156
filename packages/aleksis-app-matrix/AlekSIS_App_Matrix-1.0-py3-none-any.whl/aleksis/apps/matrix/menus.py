from django.utils.translation import gettext_lazy as _

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("Matrix"),
            "url": "#",
            "svg_icon": "simple-icons:matrix",
            "root": True,
            "validators": [
                (
                    "aleksis.core.util.predicates.permission_validator",
                    "matrix.show_menu_rule",
                ),
            ],
            "submenu": [
                {
                    "name": _("Groups and Rooms"),
                    "url": "matrix_rooms",
                    "svg_icon": "mdi:account-group-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "matrix.view_matrixrooms_rule",
                        ),
                    ],
                },
            ],
        }
    ]
}
