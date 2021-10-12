from getpass import getpass
from mysql.connector import connect, Error
from fuzzywuzzy import process
def get_details(arr):
    names_list = []
    try:
        with connect(
            host="localhost",
            user='root',
            password='10102000',
            database="plaser",
        ) as connection:
            # select_movies_query = "SELECT column5 FROM cosmetic_ingredients where column1='%s'" % (name)
            names = "select column1 from  cosmetic_ingredients"
            with connection.cursor() as cursor:
                cursor.execute(names)
                result = cursor.fetchall()
                for row in result:
                    row = row[0].replace(",","")
                    names_list.append(row)
        # print(names_list)
    except Error as e:
            print(e)
    dic = {}
    for name in arr:
        try:
            with connect(
                host="localhost",
                user='root',
                password='10102000',
                database="plaser",
            ) as connection:
                # select_movies_query = "SELECT column5 FROM cosmetic_ingredients where column1='%s'" % (name)
                with connection.cursor() as cursor:
                    str2Match = name
                    strOptions = names_list
                    Ratios = process.extract(str2Match,strOptions)
                    highest = process.extractOne(str2Match,strOptions,score_cutoff=90)
                    # print(Ratios)
                    if highest:
                        select_movies_query = "SELECT column4,column5 FROM cosmetic_ingredients where column1='%s'" % (highest[0])
                        cursor.execute(select_movies_query)
                        result = cursor.fetchall()
                        for rating,row in result:
                            # name = 
                            # print(highest[0])
                            # print(highest)
                            # print(row)
                            # print(rating)
                            # print('\n')
                            row = row.replace("\n"," ")
                            dic[highest[0]] = [rating,row]
                    else:
                        # dic[name] = ["NA","Unable to find"]
                        # print("\n")
                        continue
        except Error as e:
            print(e)
    return dic

