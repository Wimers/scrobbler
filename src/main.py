# Import modules
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialogButtonBox,
    QFileDialog,
)
from PySide6.QtCore import QThreadPool, Signal
from PySide6.QtGui import QIcon
from pathlib import Path
import sys
import os

# Import backend functions and generated UI class
from gui.interface import Ui_MainWindow
from lastfm import LastFM
from scrobbler import (
    DEFAULT_FILEPATH,
    DEFAULT_LOCAL_TZ,
)

# Page indexes
LOGIN_PAGE: int = 0
FUNCTION_PAGE: int = 1
SETTINGS_PAGE: int = 2
LOGS_PAGE: int = 3

launch_file = Path(__file__).resolve()
PROJECT_DIR = launch_file.parent.parent
ASSETS_DIR = f"{PROJECT_DIR}/assets"
CREDENTIALS_PATH = f"{PROJECT_DIR}/.user"
WINDOW_ICON_PATH = f"{ASSETS_DIR}/logo.png"
HIDDEN_ICON_PATH = f"{ASSETS_DIR}/hidden.png"
SHOW_ICON_PATH = f"{ASSETS_DIR}/show.png"
WINDOW_TITLE = "Scrobbler"
WINDOW_WIDTH = 240
WINDOW_HEIGHT = 360


class MyWindow(QMainWindow):
    signal = Signal(int)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()  # Create an instance of the UI class
        self.ui.setupUi(self)  # Set up the UI in the main window

        self._client = None
        self._password_visablity = False

        self.threadpool = QThreadPool()
        self.signal.connect(self.handle_login_outcome)

        # Sets window icon
        icon = QIcon(WINDOW_ICON_PATH)
        self.setWindowIcon(icon)

        # Connects SubmitLoginData OK to login function
        self.ui.SubmitLoginData.button(QDialogButtonBox.Save).clicked.connect(
            self.login_pressed
        )

        # Closes window if Cancel is pressed
        (
            self.ui.SubmitLoginData
            .button(QDialogButtonBox.Close)
            .clicked.connect(self.close)
        )

        # Logs out user if Logout button pressed
        self.ui.Logout.clicked.connect(self.logout)

        # Toggles password visability
        self.ui.ShowPassword.clicked.connect(self.toggle_password_visablity)

        # NEEDS TO BE IMPLEMENTED
        # self.ui.FixFile.clicked.connect(self.fix_file)

        # Sets icon for password visability, and hides button boarder
        self.ui.ShowPassword.setIcon(QIcon(HIDDEN_ICON_PATH))
        self.ui.ShowPassword.setStyleSheet("border: none;")

        self.ui.Settings.clicked.connect(self.settings)

        self.ui.ChangeFilepath.clicked.connect(self.change_filepath)
        self.ui.SaveTimezone.clicked.connect(self.change_timezone)
        self.ui.Return.clicked.connect(self.to_function_page)

        # Simulates data
        self.ui.Simulate.clicked.connect(self.simulate)
        self.ui.Verify.clicked.connect(self.verify)
        self.ui.Scrobble.clicked.connect(self.scrobble)
        self.ui.ViewLogs.clicked.connect(self.view_logs)
        self.ui.Return_1.clicked.connect(self.to_function_page)
        self.ui.ClearLog.clicked.connect(self.clear_log)

        # Sets title of Main Window
        self.setWindowTitle(WINDOW_TITLE)

        # Fixes the size of Main Window
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Sets "Login Unsuccessful" label to transparent
        self.ui.LoginFailure.setStyleSheet("color: transparent;")

        # Sets filepath text to green
        self.ui.InsertFilepath.setStyleSheet("color: green;")

        if os.path.exists(CREDENTIALS_PATH):
            self.auto_login()

    def get_client(self) -> LastFM | None:
        return self._client

    def toggle_password_visablity(self) -> None:
        if self._password_visablity:
            self.ui.ShowPassword.setIcon(QIcon(HIDDEN_ICON_PATH))
            self.ui.PasswordField.setEchoMode(
                self.ui.PasswordField.EchoMode.Password
            )
        else:
            self.ui.ShowPassword.setIcon(QIcon(SHOW_ICON_PATH))
            self.ui.PasswordField.setEchoMode(
                self.ui.PasswordField.EchoMode.Normal
            )
        self._password_visablity = not self._password_visablity

    def login_pressed(self) -> None:
        self.threadpool.start(self.attempt_manual_login)

    def attempt_manual_login(self) -> None:
        '''
        If valid credentials, logs user into account and proceeds to
        the function page. Else informs user of unsuccessful login
        attempt and clears input fields.
        '''
        user = self.ui.UserField.text().lower()
        password = self.ui.PasswordField.text()
        self._client = LastFM(
            user,
            password,
            DEFAULT_FILEPATH,
            DEFAULT_LOCAL_TZ,
        )

        sk = self.get_client().get_new_mobile_sk()

        if (sk is not None):

            # Store session key in keyring
            self.get_client().set_mobile_sk(sk)

            # Write username to file
            with open(CREDENTIALS_PATH, "w") as f:
                f.write(user)

        self.signal.emit(bool(sk))

    def handle_login_outcome(self, success: int) -> None:
        if (success):
            user = self.ui.UserField.text()
            self.login(user)
        else:
            self.ui.LoginFailure.setStyleSheet("color: red;")
        self.ui.PasswordField.clear()
        self.ui.UserField.clear()

    def auto_login(self) -> None:
        '''
        Automatically creates LastFM client based on previous login data.
        '''
        with open(CREDENTIALS_PATH, "r") as file:

            user = file.readline()
            self._client = LastFM(
                user,
                "",
                DEFAULT_FILEPATH,
                DEFAULT_LOCAL_TZ,
            )
            if (self.get_client().get_sk() is not None):
                self.login(user)

    def login(self, user) -> None:
        ''' User credentials verified, and valid client session created '''
        self.ui.stackedWidget.setCurrentIndex(FUNCTION_PAGE)
        self.ui.User.setText(u"Logged in as: " + user)
        self.ui.LoginFailure.setStyleSheet("color: transparent;")
        self._password_visablity = False

    def logout(self) -> None:
        ''' Returns to login page, and deletes credentials file '''
        self.ui.stackedWidget.setCurrentIndex(LOGIN_PAGE)

        self.get_client().delete_sk()

        # Delete file storing username
        if os.path.exists(CREDENTIALS_PATH):
            os.remove(CREDENTIALS_PATH)

    def edit_filepath_label(self) -> None:
        self.ui.InsertFilepath.setText(f"{self.get_client().get_filename()}")

    def to_function_page(self) -> None:
        self.ui.stackedWidget.setCurrentIndex(FUNCTION_PAGE)

    def settings(self) -> None:
        self.edit_filepath_label()
        self.ui.stackedWidget.setCurrentIndex(SETTINGS_PAGE)

    def view_logs(self) -> None:
        self.ui.LogData.setText(self.get_client().get_sim())
        self.ui.stackedWidget.setCurrentIndex(LOGS_PAGE)

    def simulate(self) -> None:
        self.get_client().simulate()

    def scrobble(self) -> None:
        self.get_client().scrobble()

    def verify(self) -> None:
        self.get_client().verify()

    # def fix_file(self) -> None: NEEDS IMPLIMENTATION
    #    fix_file()

    def change_filepath(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Select File',
            '',
            'Log Files (*.log)',
        )
        if (path != ''):
            self.get_client().set_filename(path)
            self.edit_filepath_label()

    def change_timezone(self) -> None:
        timezone = self.ui.Timezone.currentText()
        self.get_client().set_local_tz(timezone)
        print(self.get_client().get_local_tz())

    def clear_log(self) -> None:
        self.ui.LogData.clear()
        self.get_client().clear_simulate()


def main() -> None:
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()  # Show the main window
    sys.exit(app.exec())  # Start the application's event loop


# Run the application
if __name__ == "__main__":
    main()
