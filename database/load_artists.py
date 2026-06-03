'''
table and json file data mapping
JSON file    table
id           id
name        name
gender      gender
country     country
score      score
'''
import json
from postgres_connection import get_connection

with open("/opt/project/data/raw/artists/artists_2026_06_01.json","r") as f:
    artists = json.load(f)

conn = get_connection()
cursor = conn.cursor()

for artist in artists:
    id = artist.get("id")
    name = artist.get("name")
    gender = artist.get("gender")
    country = artist.get("country")
    score = artist.get("score")

    cursor.execute("""INSERT INTO Artists (id, name,gender,country,score) 
                   VALUES(%s,%s,%s,%s,%s)""" , 
                   (id,name,gender,country,score)
                   ) 

conn.commit()
cursor.close()
conn.close() 


