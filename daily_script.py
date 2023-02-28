import time,requests,json,pandas as pd,os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
TODAY_DATE=datetime.today().strftime('%Y-%m-%d')
import math

millnames = ['','K','M','B','Tr']

## ---API KEY->IMDB
imdb_headers = {
    'X-RapidAPI-Key': '3064429deamsh45153c39cd9e842p151c71jsn8d6daad38ccd',
    'X-RapidAPI-Host': 'online-movie-database.p.rapidapi.com'
}

List_Theater=['1025','1070','1074','1073','1072','1075']

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx]) + ' $'

def IMDB_id(row): #Get IMDB ID
  url = "https://imdb8.p.rapidapi.com/title/find"
  title=row["Title"]
  querystring = {"q":title}
  response = requests.request("GET", url, headers=imdb_headers, params=querystring)
  if ("results" in response.json()):
   results=response.json()['results'][0]['id']
   id=results.split("/")[2]
  else:
   id=""  
  return id

def IMDB_ratings(row): # Get Ratings for the movie
   title=row["Title"]
   url = "https://imdb8.p.rapidapi.com/title/get-ratings" 
   querystring = {"tconst":row['imdb_id']}
   response = requests.request("GET", url, headers=imdb_headers, params=querystring)
   try:
      return response.json()['rating']
   except:
      return 0


def IMDB_income(row): #Get Gross income worldwide
  title=row["Title"]
  url = "https://imdb8.p.rapidapi.com/title/v2/get-business"
  querystring = {"tconst":row['imdb_id']}
  response = requests.request("GET", url, headers=imdb_headers, params=querystring)
  try:
   gross=response.json()['titleBoxOffice']['gross']['aggregations'][0]['total']['amount']
  except:
   gross=0   
  return millify(gross )      
         
def YesPlanetScraper(theater_id,limit):    
# Scrape Yes Planed    
 print(theater_id+": Getting YesPlanet Info..")
 list_movie_times=[]
 list_movie_titles=[]
 list_images=[]
 url = "https://www.planetcinema.co.il/?lang=en_GB#/buy-tickets-by-cinema?in-cinema="+theater_id+"&at="+TODAY_DATE+"&view-mode=list" #Yes Planet URL
 options = Options()
 options.add_argument('--headless')
 options.add_argument('--disable-gpu')
 driver = webdriver.Chrome(options=options)
 driver.get(url)
 time.sleep(1)
 page = driver.page_source
 driver.quit()
 soup = BeautifulSoup(page, 'lxml')
 
 
 jpg_results=soup.find_all('div',class_='movie-poster-container')
 for res in jpg_results:
    image=res.find('img',class_="img-responsive")['data-src']
    title=res.find('img',class_="img-responsive")['alt']
    list_images.append([title,image])
 DF_Images=pd.DataFrame(list_images,columns=['Title','image_src'])
 results=soup.find_all('div',class_='row qb-movie')
 for movie in results:
  title=movie.find('h3','qb-movie-name').text
  list_movie_titles.append(title)
  screenings=movie.find_all('div','qb-movie-info-column')
  for s in screenings:
     if 'ATMOS' in s.text:
      list_movie_times.append([title,s.text.split(' ',1)[0]+s.text.split(' ',1)[1],s.text.split(' ',1)[2]])
     else:
      list_movie_times.append([title,s.text.split(' ',1)[0],s.text.split(' ',1)[1]])
 print(theater_id+": Finished with Yes Planet")     
 DF_Movies=pd.DataFrame(list_movie_titles,columns=['Title'])
 DF_Movie_Times=pd.DataFrame(list_movie_times,columns=['Title','Type','Time'])
 DF_Movies=DF_Movies.head(limit)        
 DF_Movies=DF_Movies.merge(DF_Images,on='Title',how='left')
 print(theater_id+": Getting IMDB Info..")     
 DF_Movies['imdb_id']=DF_Movies.apply(lambda row: IMDB_id(row),axis=1)     
 DF_Movies=DF_Movies[DF_Movies['imdb_id']!='']
 DF_Movies['imdb_ratings']=DF_Movies.apply(lambda row: IMDB_ratings(row),axis=1)
 DF_Movies['imdb_gross']=DF_Movies.apply(lambda row: IMDB_income(row),axis=1)
 print(theater_id+": Done Getting IMDB Info") 
 try:
    os.remove('pkl_files/'+theater_id+'_'+TODAY_DATE+'_movies.pkl')
    os.remove('pkl_files/'+theater_id+'_'+TODAY_DATE+'_times.pkl')
 except OSError:
    pass    
 DF_Movies.to_pickle('pkl_files/'+theater_id+'_'+TODAY_DATE+'_movies.pkl')
 DF_Movie_Times.to_pickle('pkl_files/'+theater_id+'_'+TODAY_DATE+'_times.pkl')
 
 
if __name__ == "__main__":
   # YesPlanetScraper('1070',5)
   for code in List_Theater:
      YesPlanetScraper(code,8)
      print("Saved DF'S for code "+code)
