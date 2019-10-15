import os
import img2pdf
import re
from splinter import Browser
import requests
from time import sleep, time
import argparse
import platform

system_os = platform.system()
gecko = {
    "windows":"./ressources/geckodriver.exe",
    "linux":"./ressources/geckodriver_linux",
    "darwin":"./ressources/geckodriver_mac"
}
print(system_os)
path_gecko = gecko.get(system_os.lower())
print(path_gecko)

parser = argparse.ArgumentParser(description='Recover slides from slide share')
parser.add_argument("url", type = str, 
                    help="the url of the slideshare")

parser.add_argument("--password", type=str, default = None,
                    help="Password if the file is protected")


args = parser.parse_args()

def image_to_pdf(url, password = None):
    get_image(url, password)
    def getint(text):
        return [int(i) for i in re.split("(\d+)",text) if i.isdigit() ]

    os.chdir("./tmp") 
    liste_image = [i for i in os.listdir(os.getcwd()) if i.endswith(".jpg")]
    
    liste_image.sort(key=getint)

    with open("lecture1.pdf", "wb") as f:
        f.write(img2pdf.convert([i for i in liste_image]))



def get_image(url, password = None):
    driver = Browser("firefox", executable_path=path_gecko, headless=False)
    driver.visit(url)

    if driver.find_by_id("pvtdoc") is not None:
        if password is None:
            exit('A password is requiered, please retry')
        driver.find_by_id("pvtdoc").fill(password)
        sleep(1)
        driver.find_by_value('Submit').first.click()

        sleep(2)  

        images = driver.find_by_tag('img')
        if images is None:
            exit("Wrong password, please retry")

        links = []

        for i in images:
            links.append(i['data-full'])
        links = list(filter(None, links))

        for i,link in enumerate(links):
            img_data = requests.get(link).content
            print(img_data, link)
            os.mkdir("tmp")
            with open('./tmp/'+str(i)+'.jpg', 'wb') as handler:
                handler.write(img_data)

if __name__ == "__main__":
    get_image(args.url, args.password)