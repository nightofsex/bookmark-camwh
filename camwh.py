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



screen = Screen()
prompt = PromptUtils(screen)

phpsessionid = None


class Page():
    def __init__(self, page, links, query, linksFailed: []):
        self.page = page
        self.links = links
        self.linksFailed = linksFailed
        self.query = query
    
   
    
    def printLinks(self):
        for link in self.links:
            print(f"\t{link}")
        
        

    def addBookmarkLink(self, link):
        global phpsessionid

        if manager.playlistId is not None:
            id = manager.playlistId
        else:
            id = input("Type id of playlist: ")
            manager.playlistId = id

        if phpsessionid is not None:
            phpsessid = phpsessionid
        else:
            phpsessid  = input("Type phpsessid: ")
            phpsessionid = phpsessid


        idVideo = link.split("/")[4]
        str = f"{link}?mode=async&format=json&action=add_to_favourites&video_id={idVideo}&album_id=&fav_type=10&playlist_id={id}".replace("\n", "")

        cookies = {'PHPSESSID': phpsessid}
        result = None
        try:
            result = requests.get(str,cookies = cookies)
            print(f"  {json.loads(result.content)['status']} : {link}")
            if self.linksFailed.index(link) >= 0:
                self.linksFailed.remove(link)
                manager.nLinksFailed = manager.nLinksFailed - 1
            return
        except:
            manager.areThereLinksFailed = True
            self.linksFailed.append(link)
            print(f"Non riuscito {link}")
            return 


class ManagerPage():
    
    def __init__(self, playlist = None):
        self._model = ""
        self.pages = []
        self.areThereLinksFailed = False
        self.nLinks = 0
        self.nLinksFailed = 0
        self.playlistId = playlist
    
    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, modelName):
        self._model = modelName
    
    def logPages(self):
        return f"- model: {self._model} \n - links: {self.nLinks} \n - links failed: {self.nLinksFailed}"
        

manager = ManagerPage()


def fetchLinks(q = None):

    query = None
    if q is None:
        query       = input("Query model: ")
    else:
        query = q
    
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
        try:
            res = requests.get(link)           
                
        except:
            print(f"Page failed: {page}")
            prompt.enter_to_continue() 
            return []

        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "html.parser")
            linksEl = soup.select(".list-videos a")
            return [i['href'] for i in linksEl]
        



    page = fromPage

    while page <= toPage:
        

        print(f"Fetch page: {page}")

        links = fetch()
        newPage = Page(query=query,page=page,links=links, linksFailed=[])
        manager.nLinks = manager.nLinks + len(newPage.links)
        manager.pages.append(newPage)

        newPage.printLinks()
        
        
        page = int(page) + 1

    prompt.enter_to_continue() 




def printLinks():
    for p in manager.pages:
        print(f"Fetch page: {p.page}")
        p.printLinks()

    print(manager.logPages())
    prompt.enter_to_continue() 


def saveLinks():
    
    if manager.model is "":
        manager.model = input("Model name: ")

    
    

    def obj_to_dict(obj):
        return obj.__dict__

    root = {}
    root['playlistId']  = manager.playlistId
    root['model']       = manager.model
    root[manager.model]     = []

    for page in manager.pages:
        root[manager.model].append(page.__dict__)

    with open(f"{dir}{manager.model} -test.json","w") as file:
        json.dump( root, file, indent=4)

    print("Done!")
    prompt.enter_to_continue() 



def importLinksFromFile(model = None):
    modelName = ""

    if model is None:
        modelName = input("Model name: ")
    else:
        modelName = model


    with open(f"{dir}{modelName}.json","r") as file:
        manPages = json.load(file)
  
    
   
    
    manager.model       = manPages['model']
    manager.playlistId  = manPages['playlistId']

    for page in manPages[manager.model]:
        manager.nLinks = manager.nLinks + len(page['links'])
        manager.nLinksFailed = manager.nLinksFailed + len(page['linksFailed'])
        manager.pages.append(Page(page['page'],page['links'],page['query'], page['linksFailed']))
        if manager.nLinksFailed > 0:
            manager.areThereLinksFailed = True
        
    print(f"Done! Imported:\n - pages: {len(manager.pages)}\n {manager.logPages()}")
        # print(f"Done! Imported: {len(page)} of {model}")


        

    prompt.enter_to_continue() 
    


def addBookmarks():
   
        

    for page in manager.pages:
        print(f"---- Pagina {page.page}")
        for link in page.links:
            page.addBookmarkLink(link)
    
    prompt.enter_to_continue() 

def retryBookmarkFailed():
    if manager.areThereLinksFailed is True:
        print("There aren't bookmark failed")
        return
    
    for page in manager.pages:
        nLinksFailed = len(page.linksFailed)
        if nLinksFailed == 0:
            continue

        print(f"\n---- Pagina {page.page}, n link: {nLinksFailed}")
        for link in page.linksFailed:
            print(link) 
            page.addBookmarkLink(link)
    
    prompt.enter_to_continue() 

def extractToTxt():
    
    modelName  = ""

    if manager.model is "":
        modelName = input("Model name: ")
    else:
        modelName = manager.model

    if len(manager.pages) == 0:
        print("0 model imported")
    else:
        file = open(f"{dirAllLinks}{modelName}.txt","w")
        for page in manager.pages:
            for link in page.links:
                file.write(link+"\n")
        
        file.close()
        print("Extract done")
    

    prompt.enter_to_continue() 


def menu(args):
    global phpsessionid

    if args.model:
        importLinksFromFile(args.model)

    if args.id_session:
         phpsessionid = args.id_session

    if args.playlist:
        manager.playlistId = args.playlist

    if args.query:
        fetchLinks(args.query)

    menu = ConsoleMenu("Fetch links camwhore")


    function_item1 = FunctionItem("Fetch links", fetchLinks)

    function_item2 = FunctionItem("Print links", printLinks)
    
    function_item3 = FunctionItem("Save links", saveLinks)
    
    function_item4 = FunctionItem("Import links from file", importLinksFromFile)
    
    function_item5 = FunctionItem("Add bookmarks", addBookmarks)
    
    function_item6 = FunctionItem("Retry bookmarks failed", retryBookmarkFailed)
    
    function_item7 = FunctionItem("Extract all link into file", extractToTxt)


    
    menu.append_item(function_item1)
    menu.append_item(function_item2)
    menu.append_item(function_item3)
    menu.append_item(function_item4)
    menu.append_item(function_item5)
    menu.append_item(function_item6)
    menu.append_item(function_item7)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Camwr')
    parser.add_argument('-m', '--model',
                        help='name of model to import from file')

    parser.add_argument('-q', '--query',
                        help='query to send')
    
    parser.add_argument('-p', '--playlist',
                        help='id of playlist to insert bookmark')
    
    parser.add_argument('-i', '--id-session',
                        help='id of session (phpsessionid)')

    args = parser.parse_args()


    menu(args)
    