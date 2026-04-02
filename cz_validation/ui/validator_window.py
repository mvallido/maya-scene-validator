import sys
from collections import defaultdict

import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore, QtGui
from shiboken6 import wrapInstance

from .test_case_widget import TestCaseWidget


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class CategoryHeader(QtWidgets.QWidget):

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor("#2D2D2D"))
        self.setPalette(palette)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        name = QtWidgets.QLabel(label)
        name.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 12px;")
        layout.addWidget(name)
        layout.addStretch()


class ValidatorWindow(QtWidgets.QDialog):

    INSTANCE = None

    def __init__(self, test_cases, parent=None):
        if parent is None:
            parent = get_maya_window()
        super().__init__(parent)
        self.setWindowTitle("Asset Validation")
        self.setMinimumSize(480, 520)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet("""
            QDialog { background-color: #3C3C3C; }
            QScrollArea { border: none; background-color: #3C3C3C; }
            QWidget#scroll_content { background-color: #3C3C3C; }
            QScrollBar:vertical {
                background: #3C3C3C; width: 8px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #606060; border-radius: 4px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.test_cases = test_cases
        self._test_widgets = []
        self._build_ui()

    @classmethod
    def show_window(cls, test_cases):
        if cls.INSTANCE:
            cls.INSTANCE.close()
        cls.INSTANCE = cls(test_cases)
        cls.INSTANCE.show()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._build_title())
        main_layout.addWidget(self._build_scroll_area())
        main_layout.addWidget(self._build_bottom_bar())

    def _build_title(self):
        title = QtWidgets.QLabel("Model Test Suite")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            background-color: #1E1E1E;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
        """)
        return title

    def _build_scroll_area(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QtWidgets.QWidget()
        scroll_content.setObjectName("scroll_content")
        self._test_layout = QtWidgets.QVBoxLayout(scroll_content)
        self._test_layout.setContentsMargins(0, 0, 0, 0)
        self._test_layout.setSpacing(0)

        # Group test cases by category, preserving insertion order
        grouped = defaultdict(list)
        for tc in self.test_cases:
            grouped[tc.category()].append(tc)

        for category, tests in grouped.items():
            self._test_layout.addWidget(CategoryHeader(category))
            for tc in tests:
                widget = TestCaseWidget(tc)
                self._test_widgets.append(widget)
                self._test_layout.addWidget(widget)

        self._test_layout.addStretch()
        scroll.setWidget(scroll_content)
        return scroll

    def _build_bottom_bar(self):
        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background-color: #2D2D2D;")
        layout = QtWidgets.QHBoxLayout(bar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.setMinimumWidth(90)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A4A4A;
                color: #CCCCCC;
                border: none;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5A5A5A; }
        """)
        reset_btn.clicked.connect(self._reset_all)

        run_all_btn = QtWidgets.QPushButton("Run All")
        run_all_btn.setMinimumWidth(90)
        run_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4DB6C4;
                color: #FFFFFF;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #61C4D0; }
        """)
        run_all_btn.clicked.connect(self._run_all)

        layout.addWidget(reset_btn)
        layout.addStretch()
        layout.addWidget(run_all_btn)
        return bar

    def _run_all(self):
        for widget in self._test_widgets:
            widget.run_test()

    def _reset_all(self):
        for widget in self._test_widgets:
            widget.reset()
