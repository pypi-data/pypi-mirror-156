import pandas as pd

def add_func(a:int, b:int)->int:
    """
        This function takes 2 number and returns addition of it
        Args:
            a:int : number 1
            b:int : number 2
    """
    return a + b

def sub_func(a:int, b:int)->int:
    """
        This function takes 2 number and returns substraction of it
        Args:
            a:int : number 1
            b:int : number 2
    """
    return a - b

def create_df(lst:list)->int:
    """
        This function takes 1 list of list ([[]]) and returns dataframe of it
        Args:
            a:int : number 1
    """
    return pd.DataFrame(lst)