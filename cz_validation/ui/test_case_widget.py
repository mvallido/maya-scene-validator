from PySide6 import QtWidgets, QtCore

SELECT_COL_W = 52
FIX_COL_W    = 36
INFO_COL_W   = 28
STATUS_COL_W = 20


class _InfoDialog(QtWidgets.QDialog):

    def __init__(self, test_case, parent=None):
        super().__init__(parent)
        self.setWindowTitle(test_case.name())
        self.setMinimumWidth(340)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet("""
            QDialog { background-color: #3C3C3C; }
            QLabel  { color: #CCCCCC; }
            QPlainTextEdit {
                background-color: #2D2D2D;
                color: #D45D5D;
                border: none;
                font-family: monospace;
                font-size: 11px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: #CCCCCC;
                border: none;
                padding: 5px 16px;
            }
            QPushButton:hover { background-color: #5A5A5A; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        desc = QtWidgets.QLabel(test_case.description())
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888888;")
        layout.addWidget(desc)

        if test_case._errors:
            error_header = QtWidgets.QLabel(f"Errors ({len(test_case._errors)}):")
            error_header.setStyleSheet("color: #CCCCCC; font-weight: bold;")
            layout.addWidget(error_header)

            error_box = QtWidgets.QPlainTextEdit("\n".join(test_case._errors))
            error_box.setReadOnly(True)
            error_box.setFixedHeight(min(len(test_case._errors) * 18 + 12, 200))
            layout.addWidget(error_box)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)


class TestCaseWidget(QtWidgets.QWidget):

    def __init__(self, test_case, parent=None):
        super().__init__(parent)
        self.test_case = test_case
        self._select_btn = None
        self._fix_btn = None
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(4)

        self._status_label = QtWidgets.QLabel("—")
        self._status_label.setFixedWidth(STATUS_COL_W)
        self._status_label.setAlignment(QtCore.Qt.AlignCenter)
        self._status_label.setStyleSheet("color: #555555; font-size: 11px;")
        layout.addWidget(self._status_label)

        self._name_label = QtWidgets.QLabel(self.test_case.name())
        self._name_label.setStyleSheet("color: #CCCCCC; background: transparent;")
        layout.addWidget(self._name_label, stretch=1)

        self._info_btn = QtWidgets.QPushButton("ⓘ")
        self._info_btn.setFixedSize(INFO_COL_W, 22)
        self._info_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #555555;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover { color: #999999; }
        """)
        self._info_btn.clicked.connect(self._show_info)
        layout.addWidget(self._info_btn)

        if self.test_case.is_select_errors_enabled():
            self._select_btn = QtWidgets.QPushButton("Select")
            self._select_btn.setFixedWidth(SELECT_COL_W)
            self._select_btn.setEnabled(False)
            self._select_btn.setStyleSheet(self._action_style())
            self._select_btn.clicked.connect(self.test_case.select_error_objs)
            layout.addWidget(self._select_btn)
        else:
            layout.addWidget(self._spacer(SELECT_COL_W))

        if self.test_case.is_fix_errors_enabled():
            self._fix_btn = QtWidgets.QPushButton("Fix")
            self._fix_btn.setFixedWidth(FIX_COL_W)
            self._fix_btn.setEnabled(False)
            self._fix_btn.setStyleSheet(self._action_style())
            self._fix_btn.clicked.connect(self._fix_and_retry)
            layout.addWidget(self._fix_btn)
        else:
            layout.addWidget(self._spacer(FIX_COL_W))

    def _action_style(self):
        return """
            QPushButton {
                background-color: #4A4A4A;
                color: #888888;
                border: none;
                padding: 2px 4px;
                font-size: 11px;
            }
            QPushButton:enabled:hover {
                background-color: #5A5A5A;
                color: #CCCCCC;
            }
            QPushButton:disabled {
                background-color: #3A3A3A;
                color: #4A4A4A;
            }
        """

    def _spacer(self, width):
        w = QtWidgets.QWidget()
        w.setFixedWidth(width)
        w.setStyleSheet("background: transparent;")
        return w

    def run_test(self):
        passed = self.test_case.run_test()

        if passed:
            self._status_label.setText("✓")
            self._status_label.setStyleSheet("color: #5DBD5D; font-size: 13px;")
        elif self.test_case.is_warn_on_failure():
            self._status_label.setText("⚠")
            self._status_label.setStyleSheet("color: #D4A44D; font-size: 11px;")
            if self._select_btn:
                self._select_btn.setEnabled(True)
        else:
            self._status_label.setText("✗")
            self._status_label.setStyleSheet("color: #D45D5D; font-size: 13px;")
            if self._select_btn:
                self._select_btn.setEnabled(True)
            if self._fix_btn:
                self._fix_btn.setEnabled(True)

    def reset(self):
        self.test_case.reset()
        self._status_label.setText("—")
        self._status_label.setStyleSheet("color: #555555; font-size: 11px;")
        self._name_label.setStyleSheet("color: #CCCCCC; background: transparent;")
        if self._select_btn:
            self._select_btn.setEnabled(False)
        if self._fix_btn:
            self._fix_btn.setEnabled(False)

    def _show_info(self):
        _InfoDialog(self.test_case, self).exec()

    def _fix_and_retry(self):
        self.test_case.fix_errors()
        if self.test_case.can_retry_on_fix():
            self.run_test()
