from PyQt6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy


def makeMenuLayout():
    outer = QVBoxLayout()
    outer.setContentsMargins(0, 0, 0, 0)
    outer.addStretch()

    container = QWidget()
    inner = QVBoxLayout(container)
    inner.setSpacing(20)
    inner.setContentsMargins(50, 50, 50, 50)

    container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding) 

    outer.addWidget(container)
    outer.addStretch()

    return outer, inner

def addMenuWidget(layout, widget):
    # Make widget thick and consistent
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    widget.base_min_height = 60
    widget.base_min_width = 250

    layout.addWidget(widget)

    # Force layout recalculation after insertion
    parent = layout.parentWidget()
    if parent and parent.layout():
        parent.layout().activate()
        parent.updateGeometry()

def scaleMenuWidgets(widget, scale_factor):
    layout = widget.layout()
    if not layout:
        return

    def apply_scale(layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)

            # Scale widgets
            child = item.widget()
            if child and hasattr(child, "base_min_height"):
                h = int(child.base_min_height * scale_factor)
                w = int(child.base_min_width * scale_factor)

                # Clamp to reasonable minimums
                h = max(h, 40)
                w = max(w, 120)

                # Apply scaled height
                child.setMinimumHeight(h)
                child.setMaximumHeight(h)
                child.setFixedHeight(h)

                # Apply scaled width
                child.setMinimumWidth(w)
                child.setMaximumWidth(w)

            # Scale nested layouts
            sublayout = item.layout()
            if isinstance(sublayout, QVBoxLayout):

                # --- CLAMPED MARGINS ---
                m = int(50 * scale_factor)
                m = max(m, 10)   # never go below 10px
                sublayout.setContentsMargins(m, m, m, m)

                # --- CLAMPED SPACING ---
                s = int(20 * scale_factor)
                s = max(s, 5)    # never go below 5px
                sublayout.setSpacing(s)

                apply_scale(sublayout)

    apply_scale(layout)
    widget.updateGeometry()

def finalizeMenuLayout(widget):
    layout = widget.layout()
    if layout:
        layout.activate()
    widget.updateGeometry()
