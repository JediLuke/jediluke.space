import click
import os
from bs4 import BeautifulSoup

# Finds the page's title and date
def find_page_title_date(html_filepath):
    with open(html_filepath, encoding="utf8") as html_text:
        soup = BeautifulSoup(html_text, features="html.parser")


    title = soup.find('title')
    date = soup.find('h2', class_='date')
    
    return title.text, date.text
    
def file_in_server():
    # Lists all the html files inside the directory 'blog' on the server        
        html_files = []

        with os.scandir('./articles') as files:
            for file in files:
                f = file.name
                html_files.append(f)


        return html_files

# Checks if a new html file exists in the folder "articles"
def check_new_file():
        
    path = 'blog'
    server_files = file_in_server()

    with os.scandir(path) as files:
        for file in files:
            if file.name.endswith(".html") and file.is_file():                
                print("Scraping {} for page's title and date".format(file.name))                  
                html_filepath = file.path                
                data = find_page_title_date(html_filepath)
                title, date = data
                link = html_filepath.replace(".html"," ")

     

def main():
    check_new_file()


if __name__ == '__main__':
    main()
