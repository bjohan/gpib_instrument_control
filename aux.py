
def checkParam(param, validParams, message):
    if param not in validParams:

        raise ValueError("%s. %s not in [%s]"%(message, str(param), str(validParams)))
