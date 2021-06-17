import eel
import desktop
import search

app_name="html"
end_point="index.html"
size=(700,600)

@ eel.expose
def construction_search():
    search.construction_search()

@ eel.expose
def building_search():
    search.building_search()
    
desktop.start(app_name, end_point,size)
#desktop.start(size=size,appName=app_name,endPoint=end_point)