
def validate_pk(pk):
    try:
        int(pk)
        return True
    except ValueError:
        return False
