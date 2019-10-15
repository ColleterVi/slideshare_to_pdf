import os
import img2pdf
import re
from splinter import Browser
import requests
from time import sleep, time
import argparse
import platform
from tqdm import tqdm
import shutil

system_os = platform.system()
gecko = {
    "windows":"./ressources/geckodriver.exe",
    "linux":"./ressources/geckodriver_linux",
    "darwin":"./ressources/geckodriver_mac"
}
print("Hello fellow ", system_os, ' user.')
path_gecko = gecko.get(system_os.lower())


parser = argparse.ArgumentParser(description='Recover slides from slide share')
parser.add_argument("url", type = str, 
                    help="the url of the slideshare")

parser.add_argument("--password", type=str, default = None,
                    help="Password if the file is protected")

parser.add_argument("--output", type=str, default = 'output',
                    help="name of the output file")



args = parser.parse_args()



def image_to_pdf(url, password, output):
    with Browser("firefox", executable_path=path_gecko, headless=True) as driver:

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

            if not os.path.exists("./tmp"):
                os.makedirs("./tmp")

            with tqdm(len(links)) as pbar:
                for i,link in enumerate(links):
                    pbar.set_description(f"Processing : {i}/{len(links)}")
                    img_data = requests.get(link).content

                    with open('./tmp/'+str(i)+'.jpg', 'wb') as handler:
                        handler.write(img_data)
                        
                    pbar.update(1/len(links))    

    def getint(text):
        return [int(i) for i in re.split("(\d+)",text) if i.isdigit() ]

    os.chdir("./tmp")
    liste_image = [i for i in os.listdir(os.getcwd()) if i.endswith(".jpg")]
    
    liste_image.sort(key=getint)

    with open("../"+output+".pdf", "wb") as f:
        f.write(img2pdf.convert([i for i in liste_image]))
    os.chdir('..')
    if os.path.exists("./tmp"):
        shutil.rmtree("./tmp")


if __name__ == "__main__":
    image_to_pdf(args.url, args.password, args.output)