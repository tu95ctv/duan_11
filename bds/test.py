# -*- coding: utf-8 -*-
import re
so = 5
string = u'6.200.000 đ'
kq= re.sub(u'\.|đ|\s', '',string)
# kq = kq.replace('đ','')
print kq
