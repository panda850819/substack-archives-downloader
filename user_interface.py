from downloaders.substack_archives_downloader import SubstackArchivesDownloader
from utilities import exceptions, helper
import os
from dotenv import load_dotenv

load_dotenv()



class SubstackArchivesDownloaderUserInterface:

    def __init__(self):
        self.downloader = None
        self.username = None
        self.password = None
        self.download_podcasts = False

    def get_substack_url(self) -> bool:
        while True:
            try:
                env_url = os.getenv("SUBSTACK_URL")
                if env_url:
                    input_url = env_url
                    print(f"Using Substack URL from .env: {input_url}")
                else:
                    input_url = input("Enter the URL of the Substack-hosted newsletter you would like to scrape:\n")
                
                helper.input_is_url(input_url)
                
                env_headless = os.getenv("HEADLESS")
                if env_headless is not None:
                    is_headless = env_headless.lower() == 'true'
                    print(f"Using headless mode from .env: {is_headless}")
                else:
                    while True:
                        input_is_headless = input("Would you like to see the browser while it performs the scraping? \n"
                                                  "Please type 'Y' or 'N'.\n")
                        if input_is_headless == 'Y' or input_is_headless == 'N':
                            break
                        else:
                            print("Please type 'Y' or 'N'.") # would be good to accept 'y' or 'n' etc.
                    is_headless = input_is_headless == 'N'

                if is_headless:
                    print("The browser will perform the scraping in the background.")
                else:
                    print("A new window will open during the scraping.")
                self.downloader = SubstackArchivesDownloader(input_url, is_headless)
                return True
            except exceptions.InitialisationExceptions as init_exc:
                print(init_exc)
                if os.getenv("SUBSTACK_URL"): # If env var failed, stop loop or ask for input? For now, let's just clear it and ask user.
                     print("Invalid URL in .env. Falling back to manual input.")
                     os.environ.pop("SUBSTACK_URL", None)
                     continue
                print("Please fix the error above or try again later.\n")
            except Exception as exc:
                print(exc)
                print("Unexpected error occurred while initialising.")
                return False

    def get_user_credential(self) -> bool:
        while True:
            try:
                env_email = os.getenv("SUBSTACK_EMAIL")
                env_password = os.getenv("SUBSTACK_PASSWORD")

                if env_email and env_password:
                    print("Using credentials from .env")
                    input_username = env_email
                    input_password = env_password
                else:
                    input_username = input("Please enter your Substack account email address:\n")
                    input_password = input("Please enter your Substack account password:\n")
                    # input_password = getpass(prompt="Please enter your Substack account password:\n")
                
                helper.input_email_validation(input_username)
                self.username = input_username
                self.password = input_password
                return True
            except exceptions.LoginExceptions as login_exc:
                print(login_exc)
                if os.getenv("SUBSTACK_EMAIL"):
                    print("Invalid credentials in .env. Falling back to manual input.")
                    os.environ.pop("SUBSTACK_EMAIL", None)
                    os.environ.pop("SUBSTACK_PASSWORD", None)
                    continue
                print("Please log in again or try again later.\n")
            except Exception as exc:
                print(exc)
                print("Unexpected error occurred while getting credentials.")
                self.downloader.shut_down()
                return False

    def login_using_credential(self) -> bool:
        while True:
            try:
                print("Please wait while we log in using the credential you provided...")
                self.downloader.log_in(self.username, self.password)
                print("Log in successful.")
                return True
            except exceptions.LoginExceptions as login_exc:
                print(login_exc)
                print("Please log in again or try again later.\n")
            except Exception as exc:
                print(exc)
                print("Unexpected error occurred while logging in.")
                self.downloader.shut_down()
                return False

    def get_user_download_podcasts_choice(self) -> bool:
        while True:
            try:
                env_download_podcasts = os.getenv("DOWNLOAD_PODCASTS")
                if env_download_podcasts is not None:
                    self.download_podcasts = env_download_podcasts.lower() == 'true'
                    print(f"Using podcast download setting from .env: {self.download_podcasts}")
                    return True

                while True:
                    input_is_download_podcasts = input("Would you like to download Podcast-type posts in addition to Newsletter-type posts? \n"
                                                       "Please type 'Y' or 'N'.\n")
                    if input_is_download_podcasts == 'Y' or input_is_download_podcasts == 'N':
                        break
                    else:
                        print("Please type 'Y' or 'N'.") # would be good to accept 'y' or 'n' etc.
                self.download_podcasts = input_is_download_podcasts == 'Y'
                return True
            except Exception as exc:
                print(exc)
                self.downloader.shut_down()
                return False

    # TODO decompose this method for easier debugging
    def get_user_download_choices(self) -> bool:
        while True:
            try:
                env_download_mode = os.getenv("DOWNLOAD_MODE")
                user_choice = None

                if env_download_mode:
                    print(f"Using download mode from .env: {env_download_mode}")
                    if env_download_mode == 'date_range':
                        user_choice = "1"
                    elif env_download_mode == 'count':
                        user_choice = "2"
                
                if user_choice is None:
                    print("How would you like to download the articles?")
                    print("To download articles falling within a date range, type '1'.")
                    print("To download the most recent k articles, type '2'.")
                    while True:
                        user_choice = input("Please enter your choice:\n")
                        if user_choice == "1" or user_choice == "2":
                            break
                        else:
                            print("Sorry, please either type '1' or '2'.\n")
                
                while True:
                    if user_choice == "1":
                        env_start = os.getenv("DATE_START")
                        env_end = os.getenv("DATE_END")
                        
                        if env_start and env_end:
                            date_range_start = env_start
                            date_range_end = env_end
                            print(f"Using date range from .env: {date_range_start} to {date_range_end}")
                        else:
                            print("Please specify a date range using the format YYYYMMDD.")
                            date_range_start = input("Please enter the start date: \n")
                            date_range_end = input("Please enter the end date: \n")

                        if self.validate_start_date_and_end_date(date_range_start, date_range_end):
                            # TODO covert date_ranges into something more human readable?
                            print(f"Please wait while articles published between {date_range_start} "
                                  f"to {date_range_end} are being downloaded...")
                            self.downloader.download_date_range(int(date_range_start), int(date_range_end), bool(self.download_podcasts))
                            break
                        else:
                            print("Sorry, please enter a valid date range in the format YYYYMMDD.")
                            if os.getenv("DATE_START"): # Invalid env var
                                print("Invalid date range in .env. Falling back to manual input.")
                                os.environ.pop("DATE_START", None)
                                os.environ.pop("DATE_END", None)
                                user_choice = "1" # Force loop to stay in choice 1 but manual input next time (logic a bit complex here, simplified to just ask input)
                                # Actually resetting user_choice to None might be better to restart full logic but we are inside user_choice check
                                # The simplest way is to clear env vars and let the loop run again, effectively asking for input
                                continue

                    elif user_choice == "2":
                        env_k = os.getenv("MOST_RECENT_K")
                        if env_k:
                            user_k = env_k
                            print(f"Using most recent k from .env: {user_k}")
                        else:
                            user_k = input("Please specify the number of most recent articles you'd like to download: \n")
                        
                        if self.validate_k(user_k):
                            print(f"Please wait while the {user_k} most recently published articles "
                                  "are being downloaded...")
                            self.downloader.download_k_most_recent(int(user_k), bool(self.download_podcasts))
                            break
                        else:
                            print("Sorry please enter a valid integer k.")
                            if os.getenv("MOST_RECENT_K"):
                                 print("Invalid k in .env. Falling back to manual input.")
                                 os.environ.pop("MOST_RECENT_K", None)
                                 continue

                self.downloader.shut_down()
                return True
            except Exception as exc:
                print(exc)
                self.downloader.shut_down()
                return False

    @staticmethod
    def validate_k(k: str) -> bool:
        # TODO
        # check k is an integer
        # check k is a reasonable amount (and ask the user to confirm if k is too large?)
        return True

    @staticmethod
    def validate_start_date_and_end_date(date_range_start: str, date_range_end: str) -> bool:
        # TODO
        # check each conform to yyyymmdd format
        # check date_range_start <= date_range_end
        # check that they fall within some reasonable time range (check when was Substack founded o.o)
        return True

    @staticmethod
    def validate_yyyymmdd_format(input_string: str):
        # TODO
        return True
