import requests
import re
from bs4 import BeautifulSoup
from collections import defaultdict
import time
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import pickle
import os.path

#Commencing assignment

stops = set(stopwords.words('english'))

#Data Structure of Inverted Index

class myInvertedIndex:
    def __init__(self):
        self.index = defaultdict(dict)

    def add_url(self, url, data):
        lower_data = data.lower()
        tokens = lower_data.split()
        #need to make lowercase and also disregard numbers and quotes
        filtered_tokens = [word for word in tokens if word not in stops]
        for token in filtered_tokens:
            if url not in self.index[token]:
                self.index[token][url] = 1
            else:
                self.index[token][url] += 1
    
    def printIndex(self, keyword):
        lower_keyword = keyword.lower()
        if lower_keyword not in self.index:
            print("This keyword does not exist in the inverted index")
        else:
            for x in self.index[lower_keyword]:
                print(x + " : " + str(self.index[lower_keyword][x]))

    def findIndex(self, query):
        lower_query = query.lower()
        query_tokens = lower_query.split()
        cumulative_freq = defaultdict(dict)
        for token in query_tokens:
            #Transfer documents to new combined doc_frequency list one token at a time
            if token in self.index:
                #if the token exists loop over the urls and add the respective frequencies to new dictionary
                for url in self.index[token]:
                    if url not in cumulative_freq:
                        cumulative_freq[url] = self.index[token][url]
                    else:
                        cumulative_freq[url] = cumulative_freq[url] + self.index[token][url]
        #sort the new dictionary based on cumulative frequency
        sorted_cumulative_freq = sorted(cumulative_freq.items(), key = lambda x: x[1], reverse=True)
        for x in sorted_cumulative_freq:
                print(x[0] + " : " + str(x[1]))

#define helper function for extracting all indexable text from a new link
#remove tags for style and script to leave just indexable text
def extractData(html):
    tempSoup = BeautifulSoup(html, 'html.parser')
    for script in tempSoup(["script","style"]):
        script.extract()
    return tempSoup.get_text()

traversed_urls = set()
index = myInvertedIndex()

#lets first define a crawling function
def crawl(url, depth):
    if depth <= 0:
        return
    if url in traversed_urls:
        return
    traversed_urls.add(url)
    time.sleep(6)
    html = requests.get(url).text
    data = extractData(html)
    index.add_url(url, data)
    print("Indexed a URl: " + url + " at a depth of: " + str(depth))
    #now extract all followon links
    linkSoup = BeautifulSoup(html, 'html.parser')
    totalLinks = linkSoup.find_all('a')
    for url in totalLinks:
        href = url.get('href')
        if href.startswith('/') and len(href) > 2:
            crawl("https://quotes.toscrape.com" + href, depth-1)


termination = 0
ui = ""

print("Welcome to the Web Scraping Tool")
print("Type 'build' to crawl the website, build the index, and save into an file")
print("Type 'load' to load the index from the file system")
print("Type 'print [keyword]' to print the inverted index for the particular word")
print("Type 'find [query]' to find a certain phrase in the inverted index and return a list of all pages containing that phrase")
print("Type 'exit' to exit the program")

while (termination == 0) :
    ui = input("Enter Command: ")

    #input validation and store in array for access
    #Input Validation
    val_inp = []
    val_inp = re.split(r'(\s)', ui)
    val_inp = [i for i in val_inp if i != ' ']

    if (val_inp[0] == "build"):
        crawl("https://quotes.toscrape.com/", 50)
        with open('saved_index.pkl', 'wb') as f:
            pickle.dump(index, f)
    elif (val_inp[0] == "load"):
        if(os.path.isfile('./saved_index.pkl')):
            with open('saved_index.pkl', 'rb') as f:
                index = pickle.load(f)
            print("Sucessfully Loaded")
        else:
            print("The inverted index does not exist, please build first!")
    elif (val_inp[0] == "print"):
        if(len(val_inp) == 2):
            index.printIndex(val_inp[1])
        else:
            print("Invalid command")
    elif (val_inp[0] == "find"):
        if(len(val_inp) > 1):
            temp = ""
            for i in range(1, len(val_inp)):
                temp = temp + " " + val_inp[i]
            index.findIndex(temp)
        else:
            print("Invalid command")
    elif (val_inp[0] == "exit"):
        termination = 1
    else:
        print("Invalid input")

print("Thankyou for using our client")
