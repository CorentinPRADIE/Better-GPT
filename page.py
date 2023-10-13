import requests
from bs4 import BeautifulSoup

def get_page_content(url, max):
    """
    Fetch and return the textual content of a webpage, replacing new lines with spaces.
    
    Parameters:
        url (str): The URL of the webpage to fetch content from.
        
    Returns:
        str: The textual content of the webpage, or None if fetching fails.
    """
    try:
        response = requests.get(url)
        # Ensure the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract and return the textual content of the page
            content = soup.get_text(strip=True)
            # Replace new line characters with spaces
            content_no_newlines = content.replace("\n", " ")
            content_no_newlines = ' '.join(content_no_newlines.split()[:max])
            return content_no_newlines
        else:
            print("Failed to retrieve the page: Status code", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


# url = "http://www.dateaujourdhui.com/"
# content = get_page_content(url)
# if content:
#     print(content)