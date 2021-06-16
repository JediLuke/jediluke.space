import click
import os
import html
import time
from bs4 import BeautifulSoup

"""
  This is just a test script.
"""

# Finds the page's title and date
def find_page_title_date(html_filepath):
    with open(html_filepath, encoding="utf8") as html_text:
        soup = BeautifulSoup(html_text, features="html.parser")


    title = soup.find('title')
    date = soup.find('h2', class_='date')
    
    return title.text, date.text


def insert_code(date, link, title):
  a = """
  <li>
    <aside class="dates">{0}</aside>
    <a href="./{1}"
      >{2}
      <h2></h2
    ></a>
  </li>""".format(date, link, title)

  #code = html.escape(a)

  #with open('test-index.html') as html_file:
  soup = BeautifulSoup(open('test-index.html'),'html.parser')

  ul = soup.select_one('#list')
  ul.append(BeautifulSoup('\n'+a,'html.parser'))

  new_text = soup.prettify()

  with open('test-index.html', mode='w') as new_html_file:
    new_html_file.write(new_text)



# Checks if a new html file exists in the folder "articles"
def check_new_file():
        
    path = './blog'
    i = 1

    with os.scandir(path) as files:
        click.secho("Scraping your files now for page's title and date ...", fg='bright_yellow')
        for file in files:            
            if file.name.endswith(".html") and file.is_file():            
                click.echo("File[{0}] - {1} ...".format(i,file.name))                  
                html_filepath = file.path                
                data = find_page_title_date(html_filepath)
                t, d = data
                title = t
                date = d
                i+= 1
                link = html_filepath.replace(".html", "").replace("\\", "/")                
                insert_code(date, link, title)
                time.sleep(3)
        else:
            click.secho("Contents page (index) updated successfully!", fg='bright_green')    


if __name__ == '__main__':
  check_new_file()
