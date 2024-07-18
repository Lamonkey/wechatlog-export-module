import sys
import signal
from pywxdump.analyzer.daily_diary import setup_database, get_chats_for_diary, generate_diary, setup_openai_api


def print_help():
    help_text = """
    Diary Generator Command Line Tool

    Usage:
        python diary_cli.py [OPTIONS]

    Options:
        -h, --help      Show this help message and exit

    Interactive Commands:
        Type a date (YYYY-MM-DD) to generate a diary for that date.
        Type 'exit' to exit the program.
        Press 'Ctrl+C' to exit the program safely.

    Example:
        python diary_cli.py
    """
    print(help_text)


def signal_handler(sig, frame):
    print("\nExiting safely...")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        print_help()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    db_path = input("Please enter the database path: ")
    db = setup_database(db_path)
    api_key = input("Please enter your OpenAI API key: ")
    client = setup_openai_api(api_key)

    if not db.is_table_exist('WL_MSG'):
        raise ValueError(
            "Database does not contain the required table 'WL_MSG'.")

    while True:
        date = input(
            "Please enter the date (YYYY-MM-DD) or type 'exit' to quit: ")
        if date.lower() == 'exit':
            print("Exiting...")
            break
        try:
            text_log = get_chats_for_diary(db, db_path, date)
            print(generate_diary(text_log, client) + "\n")
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        except Exception as e:
            print(f"An error occurred: {e}")
