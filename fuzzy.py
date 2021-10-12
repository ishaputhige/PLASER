def get_details(arr):
    from getpass import getpass
    from mysql.connector import connect, Error
    from fuzzywuzzy import process
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
                        if len(name) > 22:
                            pass
                        else:
                            dic[name] = ["NA","Unable to find"]
                        # print("\n")
        except Error as e:
            print(e)
    print(dic)



arr = ['Aqua', 'Glycerin', 'Stearic Acid', 'Lauric Acid', 'Myristic Acid', 'Potassium Laureth Phosphate', 'Potassium a Hydroxide', 'Palmitic Acid', 'Ceteareth25', 'Sodium Cocoyl oo Glycinate', 'Glycol Distearate', 'Hydrogenated Castor Oil', 'an Tremella Fuciformis Sporocarp Extract', 'Dendrobium is Candidum Extract', 'Sodium Taurine Laurate', 'a ee Polyquatemium7', 'Charcoal Powder', 'Com Starch ot Modified', 'Sodium Hydroxymethyiglycinate', 'Hydroxypropy  Methyicellulose', 'Disodium EDTA', 'Tocopherol', 'Acetyi i Glucosamine', 'Aroma etcreger Store t Ke ealty placer Avold oy cunight en yhigh temperature Sy _ a  Manufacture Date SODMMYYYYAS shown on the package Sam oo Expiration Date DDMMIYYYY As shown on the package aaa  cage ta RS Ns cmemekiflpuiner tal onercemecmatieee Pe  CEES LSD Guangdong Essence Dally ily Chemical a Co ances OKETEY Road Shenshan Administrative Bia Area J langgao Ja0', 'Town eaiyun Distric i Guangzhou City SaaCne  Guangdon ng Province China oe aa fiiow to Users Apply appropriate amount onto wet skir io eg Med ayay  Cael   gay massage inva a circular movement rinse off be  CutioniFor oxternal use joniysAvold contact ran ha Ss  SUE uct gets Into eyes MNT withw wale Sr a sential call  mage a Immediately Piease keep it out of reach of children', 'ry qhsonuit guse if signs of irritation orrash appeals oe om', 'allowed seek medical assistance iis enibe Planiaciae Tor SRTRe Scr Fabtcado para NO IM ye']
get_details(arr)