def join_array(array, separator=','):
    txtOut=""
    for i,genre in enumerate(array):
        txtOut += genre
        if i != len(array) -1:
            txtOut+=separator
    print(txtOut)     
    return txtOut

def map_attribute(source , destination , attributes_):
    """
    @summary: maps the attributes from source to destination by setting the 
    corresponding attributes at the destination to the corresponding value in the 
    source 
    """
    for attr in attributes_:
        field = getattr(destination, attr)
        field.data = getattr(source, attr)