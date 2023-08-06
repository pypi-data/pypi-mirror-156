def ind_time_convert(h,m,s):

    h = h+5
    m = m+30
    if h>23:
        h = h-24  
    if m>60:
        h = h+1
        m = m-60



    if h<10:
        h = '0'+str(h)
 
    else:
        h = str(h)

    if m<10:
        m = '0'+str(m)
    else:
        m = str(m)
    time = h+m+s


    return time