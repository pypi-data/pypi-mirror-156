"""validate_input.

This function will validate input.
"""


def validate_input(prompt, options):
    """Validate the input from the user.

    :param options: a list of eligible options.
    """
    while True:
        try:
            option = input(prompt).lower()
        except KeyboardInterrupt:
            quit()

        if option in options:
            return option
        elif option == "quit":
            quit()

        print("Sorry, I didn't understand! Try Again!")
