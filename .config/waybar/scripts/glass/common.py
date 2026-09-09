"""Base compartida para los popups Liquid Glass (reemplazo GTK de wofi/rofi)."""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gtk, Gdk, GLib, GtkLayerShell

THEME_CSS = __file__.rsplit("/", 1)[0] + "/theme.css"

_css_loaded = False


def _load_css():
    global _css_loaded
    if _css_loaded:
        return
    provider = Gtk.CssProvider()
    provider.load_from_path(THEME_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
    _css_loaded = True


class GlassPopup(Gtk.Window):
    """Ventana capa (layer-shell), sin bordes, con fondo translúcido real
    y blur del compositor via layerrule namespace 'glass-menu'."""

    def __init__(self, title="", width=300, margin_right=10, center=False, height=-1):
        super().__init__()
        _load_css()

        self.set_decorated(False)
        self.set_default_size(width, height)
        self.set_resizable(False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.get_style_context().add_class("glass-panel")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "glass-menu")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        if not center:
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 36)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, margin_right)

        self.connect("key-press-event", self._on_key)
        self.connect("draw", self._on_draw)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        if title:
            title_lbl = Gtk.Label(xalign=0)
            title_lbl.set_markup(title)
            title_lbl.get_style_context().add_class("glass-title")
            outer.pack_start(title_lbl, False, False, 0)
        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer.pack_start(self.body, True, True, 0)
        self.add(outer)

    def _on_draw(self, widget, cr):
        # app_paintable(True) disables GTK's automatic CSS background paint for
        # windows, so without this the panel stays fully transparent and only
        # child widgets with their own background (hover states, etc.) show.
        context = widget.get_style_context()
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        Gtk.render_background(context, cr, 0, 0, width, height)
        Gtk.render_frame(context, cr, 0, 0, width, height)
        return False

    def _quit(self):
        Gtk.main_quit()
        return False

    def _on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self._quit()
        return False

    def run(self):
        self.show_all()
        self.present()
        Gtk.main()


def make_list():
    box = Gtk.ListBox()
    box.set_selection_mode(Gtk.SelectionMode.NONE)
    box.get_style_context().add_class("glass-list")
    return box


def add_row(listbox, glyph, label, meta="", danger=False, active=False, on_click=None):
    row = Gtk.ListBoxRow()
    row.set_activatable(True)
    if danger:
        row.get_style_context().add_class("danger")
    if active:
        row.get_style_context().add_class("active")

    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox.set_margin_top(6)
    hbox.set_margin_bottom(6)
    hbox.set_margin_start(6)
    hbox.set_margin_end(6)

    glyph_lbl = Gtk.Label(label=glyph)
    glyph_lbl.get_style_context().add_class("row-glyph")
    hbox.pack_start(glyph_lbl, False, False, 0)

    text_lbl = Gtk.Label(label=label, xalign=0)
    text_lbl.get_style_context().add_class("row-label")
    hbox.pack_start(text_lbl, True, True, 0)

    if meta:
        meta_lbl = Gtk.Label(label=meta)
        meta_lbl.get_style_context().add_class("row-meta")
        hbox.pack_start(meta_lbl, False, False, 0)

    row.add(hbox)
    listbox.add(row)

    if on_click:
        row._on_click = on_click
    return row


def bind_activate(listbox, popup):
    def handler(_lb, row):
        cb = getattr(row, "_on_click", None)
        if cb:
            cb()
            popup._quit()

    listbox.connect("row-activated", handler)


def sep():
    s = Gtk.Box()
    s.get_style_context().add_class("glass-sep")
    return s


def section_label(text):
    lbl = Gtk.Label(label=text, xalign=0)
    lbl.get_style_context().add_class("glass-section-label")
    return lbl
