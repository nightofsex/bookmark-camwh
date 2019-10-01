""" 
    pip install beautifulsoup4
    pip install console-menu

    let ul = document.querySelector("body > div.container > div.content > div.block-video > div > div.video-info > div > div.info-buttons > div.btn-favourites > ul")
        ul.style.position = "fixed"
        ul.style.display="block"
        ul.style.top="0"
        ul.style.overflow ="auto"
        ul.style.width="200px"
        ul.style.height="100%"
"""
import argparse
import json
import requests
from bs4 import BeautifulSoup
import os
import time
from consolemenu import *
from consolemenu.items import *


filename = "links_camwr.json"
dir = "links/"
dirAllLinks = dir

# if os.path.exists(filename):
#     os.remove(filename)



# file = open("links_camwr.txt","a")


pages = []
screen = Screen()
prompt = PromptUtils(screen)
playlistId = None
phpsessionid = None

# def fetchpage(page):
#     link = f"http://www.camwhores.tv/search/evad/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q=evad&category_ids=&sort_by=&from_videos={page}&from_albums={page}&_=1569846080479"
#     result = requests.get(link)

#     while True:
#         if result.status_code == 200:
#             c = result.content

#             soup = BeautifulSoup(c, "html.parser")
#             links = soup.select(".list-videos a")
#             print(f"---- Pagina {page}")

            
#             for link in links:
#                 str = link['href']
#                 file.write(str+"\n")
#                 print(str)
#                 linksAll.append(str)

#             nextpage(page)
#             break


# def addBookmarks(linksAll):
#     for link in linksAll:
#         id = link.split("/")[4]
#         str = f"{link}?mode=async&format=json&action=add_to_favourites&video_id={id}&album_id=&fav_type=10&playlist_id={playlistId}".replace("\n", "")
#         cookies = {'PHPSESSID': '50vofcde8oqogd4ls27ojki1rl'}
        
#         result = requests.get(str,cookies = cookies)
#         print(id +" "+ result.content.status + linksAll.index(link))
#         # time.sleep(1)
#         # return

# def nextpage(page):
#     page = page + 1
#     if page == MAX_PAGE:
#         return
#     fetchpage(page)


class Page():
    def __init__(self, page, links, query):
        self.page = page
        self.links = links
        self.query = query
    
    
    def printLinks(self):
        for link in self.links:
            print(f"\t{link}")

class ManagerPage():
    
    def __init__(self):
        self._model = ""
        self.pages = []
    
    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, modelName):
        self._model = modelName
        

manager = ManagerPage()


def fetchLinks():
    # pages = []

    

    query       = input("Query model: ")
    fromPage    = input("From page(1): ")
    toPage      = input("To page(1): ")
    


    if fromPage is '':
        fromPage = 1
    else:
        fromPage = int(fromPage)
        
    
    if toPage is '':
        toPage = 1
    else:
        toPage = int(toPage)


    def fetch():
        link = f"http://www.camwhores.tv/search/{query}/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q={query}&category_ids=&sort_by=&from_videos={page}&from_albums={page}&_=1569846080479"
        res = requests.get(link)
        while True:
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")
                linksEl = soup.select(".list-videos a")
                return [i['href'] for i in linksEl]
        
        



    page = fromPage

    while page <= toPage:
        

        print(f"Fetch page: {page}")

        links = fetch()
        newPage =  Page(query=query,page=page,links=links)
        pages.append(newPage)

        newPage.printLinks()
        
        
        page = int(page) + 1

    prompt.enter_to_continue() 




def printLinks():
    for p in pages:
        print(f"Fetch page: {p.page}")
        p.printLinks()
    prompt.enter_to_continue() 


def saveLinks():

    modelName = input("Model name: ")
    

    def obj_to_dict(obj):
        return obj.__dict__

    manager.model = modelName
    root = {}
    root[modelName] = []
    for page in pages:
        root[modelName].append(page.__dict__)

    with open(f"{dir}{modelName}.json","w") as file:
        json.dump( root, file, indent=4)

    print("Done!")
    prompt.enter_to_continue() 



def importLinksFromFile(model: None):
    modelName = ""

    if model is None:
        modelName = input("Model name: ")
    else:
        modelName = model


    with open(f"{dir}{modelName}.json","r") as file:
        p = json.load(file)
  
    
   

    for model in p:
        manager.model = model
        page = p[model]
        for p in page:
            pages.append(Page(p['page'],p['links'],p['query']))
        
    print(f"Done! Imported: {len(pages)} of {model}")
        # print(f"Done! Imported: {len(page)} of {model}")


        

    prompt.enter_to_continue() 
    


def addBookmarks():
    global phpsessionid, playlistId

    if playlistId is not None:
        id = playlistId
    else:
        id = input("Type id of playlist: ")

    if phpsessionid is not None:
        phpsessid = phpsessionid
    else:
        phpsessid  = input("Type phpsessid: ")

    def addBookmarkLink(link):
        idVideo = link.split("/")[4]
        str = f"{link}?mode=async&format=json&action=add_to_favourites&video_id={idVideo}&album_id=&fav_type=10&playlist_id={id}".replace("\n", "")

        cookies = {'PHPSESSID': phpsessid}
        try:
            result = requests.get(str,cookies = cookies)
            print(f"  {json.loads(result.content)['status']} : {link}")
        except:
            print(f"Non riuscito {link}")
        

    for page in pages:
        print(f"---- Pagina {page.page}")
        for link in page.links:
            addBookmarkLink(link)
    
    prompt.enter_to_continue() 

def extractToTxt():
    
    modelName  = ""

    if manager.model is "":
        modelName = input("Model name: ")
    else:
        modelName = manager.model

    if len(pages) == 0:
        print("0 model imported")
    else:
        file = open(f"{dirAllLinks}{modelName}.txt","w")
        for page in pages:
            for link in page.links:
                file.write(link+"\n")
        
        file.close()
        print("Extract done")
    

    prompt.enter_to_continue() 


def menu(args):
    global phpsessionid, playlistId

    if args.model:
        importLinksFromFile(args.model)

    if args.id_session:
         phpsessionid = args.id_session

    if args.playlist:
        playlistId = args.playlist


    menu = ConsoleMenu("Fetch links camwhore")


    function_item1 = FunctionItem("Fetch links", fetchLinks)

    function_item2 = FunctionItem("Print links", printLinks)
    
    function_item3 = FunctionItem("Save links", saveLinks)
    
    function_item4 = FunctionItem("Import links from file", importLinksFromFile)
    
    function_item5 = FunctionItem("Add bookmarks", addBookmarks)
    
    function_item6 = FunctionItem("Extract all link into file", extractToTxt)


    
    menu.append_item(function_item1)
    menu.append_item(function_item2)
    menu.append_item(function_item3)
    menu.append_item(function_item4)
    menu.append_item(function_item5)
    menu.append_item(function_item6)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Camwr')
    parser.add_argument('-m', '--model',
                        help='name of model to import from file')
    
    parser.add_argument('-p', '--playlist',
                        help='id of playlist to insert bookmark')
    
    parser.add_argument('-i', '--id-session',
                        help='id of session (phpsessionid)')

    args = parser.parse_args()


    menu(args)
    