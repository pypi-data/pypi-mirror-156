import validators


def extract_valid_url(url: str):
    first_url = get_first_url_if_has_more_than_one(url)
    if validators.url(first_url) is not True:
        return change_url_to_right_pattern(first_url)
    return first_url


def get_first_url_if_has_more_than_one(url: str):
    if has_character(url, ","):
        return url.split(",")[0]
    if has_character(url, ";"):
        return url.split(";")[0]
    if has_character(url, " "):
        return url.split(" ")[0]
    return url


def has_character(url: str, character: str):
    return url.find(character) is not -1


def change_url_to_right_pattern(url: str):
    if is_instagram_user(url):
        url = url.replace("@", "https://www.instagram.com/")
    if not is_valid_url(url):
        url = f"https://{url}"
    return url


def is_instagram_user(url: str):
    return url.startswith("@")


def is_valid_url(url):
    return url.startswith("https")
