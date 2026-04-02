def show():
    from .ui.validator_window import ValidatorWindow
    from .test_cases import all_test_cases
    ValidatorWindow.show_window(all_test_cases())
