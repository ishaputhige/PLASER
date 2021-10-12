import re
def post_ocr(st1):
    exp=r"[^a-zA-z0-9, ]"
    exp2=r"[/[ /]]"
    a=re.sub(exp,'',st1)
    a=re.sub(exp2,'',a)
    e1=r"(?i)ingredients|content|contents|ingredient"
    s=re.search(e1,a)
    m=s.span()
    a=a[m:]
    l=[x.strip() for x in re.split(',',a)]
    print(l)
    return l
