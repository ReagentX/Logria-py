from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.document import Document
from prompt_toolkit.layout.margins import ScrollbarMargin

from logria.interface.titles import get_titlebar_text

def build_app():
    # Create document instances
    left_doc = Document(text='Hello world\n' * 1000 + 'End')
    right_doc = Document(text='\n' * 25)

    # Window buffers
    left_buffer = Buffer()
    right_buffer = Buffer()
    left_buffer.set_document(left_doc)
    right_buffer.set_document(right_doc)

    # scrollbar
    scrollbar = ScrollbarMargin(display_arrows=True)

    # Hand control over
    left_window = Window(BufferControl(buffer=left_buffer), right_margins=[scrollbar], wrap_lines=True)
    right_window = Window(BufferControl(buffer=right_buffer), right_margins=[scrollbar], wrap_lines=True)

    # UI stuff
    body = VSplit(
        [
            left_window,
            Window(width=1, char="|", style="class:line"),
            right_window,
        ]
    )
    root_container = HSplit(
        [
            Window(
                height=1,
                content=FormattedTextControl(get_titlebar_text),
                align=WindowAlign.CENTER,
            ),
            Window(height=1, char="–", style="class:line"),
            body,
        ]
    )

    # Key bindings
    kb = KeyBindings()

    @kb.add("c-c", eager=True)
    @kb.add("c-q", eager=True)
    def _(event):
        """
        Pressing Ctrl-Q or Ctrl-C will exit the user interface.
        """
        event.app.exit()

    application = Application(
        layout=Layout(root_container, focused_element=right_window),
        key_bindings=kb,
        mouse_support=True,
        full_screen=True,
    )
    return application
