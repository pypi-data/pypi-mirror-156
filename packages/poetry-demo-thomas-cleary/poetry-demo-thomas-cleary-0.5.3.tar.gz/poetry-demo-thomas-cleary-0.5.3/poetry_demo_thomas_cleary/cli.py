from .example_functions import add_one, get_txt_data, get_google_response_status_code


def run():
    num = 1
    print("This is a cli script for the poetry-demo-thomas-cleary python package.")
    print(
        f"The number {num} can be incremented with the example_functions.add_one() to {add_one(num)}."
    )
    print(f"{get_txt_data()} (read for package data.txt file)")
    print(f"GET www.google.com: {get_google_response_status_code()}")
