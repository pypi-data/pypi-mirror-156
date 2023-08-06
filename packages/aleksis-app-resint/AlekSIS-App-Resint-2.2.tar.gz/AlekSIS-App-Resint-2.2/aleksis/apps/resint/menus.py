from typing import Any, Dict, List

from django.apps import apps
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


def _get_menu_entries() -> List[Dict[str, Any]]:
    """Build menu entries for all poster groups.

    This will include only poster groups where ``show_in_menu`` is enabled.
    """
    PosterGroup = apps.get_model("resint", "PosterGroup")
    return [
        {
            "name": group.name,
            "url": reverse("poster_show_current", args=[group.slug]),
            "icon": "picture_as_pdf",
            "validators": [
                (
                    "aleksis.apps.resint.rules.permission_validator",
                    "resint.view_poster_pdf_menu",
                    group,
                ),
            ],
            "new_tab": True,
        }
        for group in PosterGroup.objects.all()
    ]


class MENUS:
    def get(menu_name, default=None):
        menus = {
            "NAV_MENU_CORE": [
                {
                    "name": _("Documents"),
                    "url": "#",
                    "icon": "open_in_browser",
                    "root": True,
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "resint.view_poster_menu",
                        ),
                    ],
                    "submenu": [
                        {
                            "name": _("Manage posters"),
                            "url": "poster_index",
                            "icon": "file_upload",
                            "validators": [
                                (
                                    "aleksis.core.util.predicates.permission_validator",
                                    "resint.view_posters_rule",
                                ),
                            ],
                        },
                        {
                            "name": _("Poster groups"),
                            "url": "poster_group_list",
                            "icon": "topic",
                            "validators": [
                                (
                                    "aleksis.core.util.predicates.permission_validator",
                                    "resint.view_postergroups_rule",
                                ),
                            ],
                        },
                        {
                            "name": _("Live documents"),
                            "url": "live_documents",
                            "icon": "update",
                            "validators": [
                                (
                                    "aleksis.core.util.predicates.permission_validator",
                                    "resint.view_livedocuments_rule",
                                ),
                            ],
                        },
                    ],
                }
            ]
            + _get_menu_entries(),
        }

        return menus.get(menu_name, default)
