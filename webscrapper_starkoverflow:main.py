#main.py

from flask import Flask, render_template, request, redirect, send_file
from templates.scrapper import get_jobs
from exporter import save_to_file
app = Flask("SuperScrapper")

db = {}

@app.route("/")
def home():
  return render_template('home.html')

@app.route("/report")
def report():
  word = request.args.get('word')
  if word:
    word = word.lower()
    exis = db.get(word)
    if exis:
      jobs = exis
      
    else:
      jobs = get_jobs(word)
    db[word] = jobs
  else:
    return redirect("/")


  return render_template("report.html", searchingby=word,
  resultsNumber=len(jobs), jobs=jobs)
  
 

@app.route("/export")


def export():
  try:
    word = request.args.get('word')
    if not word:
      raise Exception()
    word = word.lower()
    jobs = db.get(word)
    if not jobs:
      raise Exception()
    save_to_file(jobs)  
    return send_file("jobs.csv")
  except:
    return redirect("/")
      
app.run(host="0.0.0.0")

# scrapper
import requests
from bs4 import BeautifulSoup



def get_last_page(url):
  result = requests.get(url)
  soup = BeautifulSoup(result.text, "html.parser")
  pages = soup.find("div",{"class":"s-pagination"}).find_all("a")
  last_page = pages[-2].get_text(strip=True)
  return int(last_page)

def extract_job(html):
  title = html.find("h2",{"class":"mb4"}).find("a")["title"]
  company, location = html.find("h3",{"class":"mb4"}).find_all("span",recursive=False)
  company = company.get_text(strip=True)
  location = location.get_text(strip=True)
  job_id = html['data-jobid']

  return {'title': title, 'company' : company, "location" : location, 'link' : f"https://stackoverflow.com/jobs/{job_id}"}




def extract_jobs(last_page, url):
  jobs = []
  for page in range(last_page):
    print(f"Scrapping SO : page:{page}")
    result = requests.get(f"{url}&pg={page+1}")
    soup = BeautifulSoup(result.text,"html.parser")
    results = soup.find_all("div", {"class":"-job"})
    
    
  for result in results:
      job = extract_job(result)
      jobs.append(job)
     
  return jobs  


   


def get_jobs(word):
  url = f"https://stackoverflow.com/jobs?q={word}&pg=i"
  last_page = get_last_page(url)
  jobs = extract_jobs(last_page, url)
  return jobs

#exporter
import csv

def save_to_file(jobs):
  file = open("jobs.csv", mode="w", encoding='utf-8')
  writer = csv.writer(file)
  writer.writerow(["title", "company","location","link"])
  for job in jobs:
    writer.writerow(list(job.values()))
  return
  
#html_template
<!DOCTYPE html>
<html>
  <head>
    <title>Jbo Search</title>
  </head>
  <body>
    <h1>Job Search</h1>
    <form action="/report" method="get">
      <input placeholder='Search for a job' required name="word" />
      <button>Search</button>
      </form>
  </body>
</html>

#html_report
<!DOCTYPE html>
<html>
  <head>
    <title>Jbo Search</title>
    <style>
      section{
        display:grid;
        gap : 20px;
        grid-template-columns: repeat(4, 1fr);
      }
      
    </style>
  </head>
  <body>
   <h1>Search Results</h1>
   <h3>Found {{resultsNumber}} results for: {{searchingby}} </h3>
   <a href="/export?word={{searchingby}}">Export to CSV</a>
   <section>
     <h4>Title</h4>
     <h4>Company</h4>
     <h4>Location</h4>
     <h4>Link</h4>
     {% for job in jobs%}
     <span>{{job.title}}</span>
     <span>{{job.company}}</span>
     <span>{{job.location}}</span>
     <a href="{{job.link}}" target="blank">Apply</a>
     
     {%endfor%}

  </body>
</html>






