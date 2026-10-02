"""Launch the AI Fruit Cutter game."""


def main():
    """Start the webcam-powered game UI."""
    from ui.ui_controller import UIController

    UIController().run()


if __name__ == "__main__":
    main()
