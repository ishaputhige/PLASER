from config import Config
from dotenv import load_dotenv
import pymysql
from collections import OrderedDict

def get_details(arr,mysql):
    from getpass import getpass
    from mysql.connector import connect, Error
    from rapidfuzz import process
    arr.sort()
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
    red_names = []
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
                    red_names.append(name)
                # print("\n")
        except Error as e:
            print(e)
    for name in red_names:
        dic[name] = ["NA","Unable to find"]
    count_dic = {"Best":0,"Good":0,"Poor":0,"NA":0}
    for i in dic.keys():
        if dic[i][0] not in count_dic:
            count_dic[dic[i][0]] = 1
        else:
            count_dic[dic[i][0]] += 1
    print(dic.keys())
    count_dic = OrderedDict(sorted(count_dic.items()))
    print(count_dic)
    return dic,count_dic
