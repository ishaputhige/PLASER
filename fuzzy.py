from config import Config
from dotenv import load_dotenv
import pymysql

def get_details(arr,mysql):
    from getpass import getpass
    from mysql.connector import connect, Error
    from rapidfuzz import process
    names_list = []
    ingred_dic = {}
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # select_movies_query = "SELECT column5 FROM cosmetic_ingredients where column1='%s'" % (name)
        query = "select name,rating,description from  cosmetic_ingredients"
        # with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        # print(result)
        for row in result:
            # print("heelllo",row)
            # row = row['name']
            # print(row)
            ingred_dic[row['name']] = [row['rating'],row['description']]
            # print(name,rating,description)
            # names_list.append(row)
        # print(ingred_dic)
    except Error as e:
            print(e)
    dic = {}
    print(1)
    strOptions = ingred_dic.keys()
    # print(strOptions)
    for name in arr:
        try:
            # with connect(
            #     host="localhost",
            #     user='root',
            #     password='10102000',
            #     database="plaser",
            # ) as connection:
            #     # select_movies_query = "SELECT column5 FROM cosmetic_ingredients where column1='%s'" % (name)
            #     with connection.cursor() as cursor:
            str2Match = name
            # Ratios = process.extract(str2Match,strOptions)
            highest = process.extractOne(str2Match,strOptions,score_cutoff=90)
            # print(Ratios)
            if highest:
                # select_movies_query = "SELECT column4,column5 FROM cosmetic_ingredients where column1='%s'" % (highest[0])
                # cursor.execute(select_movies_query)
                
                # result = cursor.fetchall()
                # for rating,row in result:
                    # name = 
                    # print(highest[0])
                    # print(highest)
                    # print(row)
                    # print(rating)
                    # print('\n')
                    # row = row.replace("\n"," ")
                    dic[highest[0]] = [ingred_dic[highest[0]][0],ingred_dic[highest[0]][1]]
            else:
                if len(name) > 22:
                    pass
                else:
                    dic[name] = ["NA","Unable to find"]
                # print("\n")
        except Error as e:
            print(e)
    print(dic.keys())
    return dic
