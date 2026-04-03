from PyQt6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QPushButton

# Default button sizes for consistency
DEFAULT_BUTTON_WIDTH = 250
DEFAULT_BUTTON_HEIGHT = 80
DEFAULT_LAYOUT_MARGIN = 50
DEFAULT_LAYOUT_SPACING = 20


def makeMenuLayout() -> tuple[QVBoxLayout, QVBoxLayout]:
    outer = QVBoxLayout()
    outer.setContentsMargins(0, 0, 0, 0)
    outer.addStretch()

    container = QWidget()
    inner = QVBoxLayout(container)
    inner.setSpacing(DEFAULT_LAYOUT_SPACING)
    inner.setContentsMargins(DEFAULT_LAYOUT_MARGIN, DEFAULT_LAYOUT_MARGIN,
                             DEFAULT_LAYOUT_MARGIN, DEFAULT_LAYOUT_MARGIN)

    container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)

    outer.addWidget(container)
    outer.addStretch()

    return outer, inner


def addMenuWidget(layout, widget: QWidget):
    """
    Add a widget to the menu layout and enforce consistent thickness and size.
    Works for buttons, sliders, or any QWidget.
    """
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    # Force min/max/fixed size for consistent thickness
    widget.setMinimumSize(DEFAULT_BUTTON_WIDTH, DEFAULT_BUTTON_HEIGHT)
    widget.setMaximumSize(DEFAULT_BUTTON_WIDTH, DEFAULT_BUTTON_HEIGHT)
    widget.setFixedSize(DEFAULT_BUTTON_WIDTH, DEFAULT_BUTTON_HEIGHT)

    # Store base sizes for optional scaling later
    widget.base_min_height = DEFAULT_BUTTON_HEIGHT
    widget.base_min_width = DEFAULT_BUTTON_WIDTH

    layout.addWidget(widget)

    # Force layout recalculation
    parent = layout.parentWidget()
    if parent and parent.layout():
        parent.layout().activate()
        parent.updateGeometry()


def scaleMenuWidgets(widget, scale_factor):
    """
    Recursively scales all menu widgets according to a factor.
    Keeps a minimum width/height and spacing.
    """
    layout = widget.layout()
    if not layout:
        return

    def apply_scale(layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)

            # Scale widgets
            child = item.widget()
            if child and hasattr(child, "base_min_height"):
                h = max(int(child.base_min_height * scale_factor), 40)
                w = max(int(child.base_min_width * scale_factor), 120)
                child.setMinimumSize(w, h)
                child.setMaximumSize(w, h)
                child.setFixedSize(w, h)

            # Scale nested layouts
            sublayout = item.layout()
            if isinstance(sublayout, QVBoxLayout):
                m = max(int(DEFAULT_LAYOUT_MARGIN * scale_factor), 10)
                s = max(int(DEFAULT_LAYOUT_SPACING * scale_factor), 5)
                sublayout.setContentsMargins(m, m, m, m)
                sublayout.setSpacing(s)
                apply_scale(sublayout)

    apply_scale(layout)
    widget.updateGeometry()


def finalizeMenuLayout(widget):
    """
    Recalculates and finalizes the menu layout.
    """
    layout = widget.layout()
    if layout:
        layout.activate()
    widget.updateGeometry()


def clear_layout(layout):
    """
    Recursively removes all widgets and spacers from a layout.
    """
    if layout is None:
        return

    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().setParent(None)
        elif item.layout():
            clear_layout(item.layout())