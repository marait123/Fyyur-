def join_array(array, separator=','):
    txtOut=""
    for i,genre in enumerate(array):
        txtOut += genre
        if i != len(array) -1:
            txtOut+=separator
    print(txtOut)     
    return txtOut