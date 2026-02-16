from weakref import WeakSet

_registered_menus = WeakSet()

def register_menu(menu):
    """Track all menu instances that should refresh on language change."""
    _registered_menus.add(menu)

def refresh_all_menus():
    """Tell every registered menu to reload texts."""
    for menu in list(_registered_menus):
        if hasattr(menu, "_reload_texts"):
            menu._reload_texts()