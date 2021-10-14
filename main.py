import gi
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from subprocess import PIPE, Popen


class App(Gtk.Window):
    """The application window."""

    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect("delete-event", self.quit)

        self.previous_line = ""

        # The box to hold the widgets in the window
        self.box = Gtk.VBox()
        self.add(self.box)

        # The text widget to output the log file to
        self.text = Gtk.TextView()
        self.text.set_editable(False)
        self.box.pack_start(self.text, True, True, 0)

        self.start_timer()

        self.show_all()

    def start_timer(self):
        self.timer = threading.Timer(1, self.read_log)
        self.timer.start()

    def quit(self, *args):
        """Quit."""
        # Stop the timer, in case it is still waiting when the window is closed
        self.timer.cancel()
        Gtk.main_quit()

    def read_log(self):
        """Read the log."""

        p = Popen(["journalctl", "--user-unit=onedrive"], stdout=PIPE)
        with p.stdout:
            for line in iter(p.stdout.readline, b''):
                current_line = line.decode("utf-8")
        p.wait()

        # format string for output
        parts = current_line.split(']:')

        if len(parts) < 2:
            output = current_line
        else:
            output = parts[1]

        if current_line != self.previous_line:
            self.previous_line = current_line
            self.text.set_editable(True)
            self.text.get_buffer().insert_at_cursor(output)
            self.text.set_editable(False)

        # Reset the timer
        self.start_timer()


if __name__ == "__main__":
    app = App()
    Gtk.main()
