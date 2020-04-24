class BaseFactory(object):
    """
    Object inherited class defines a POM structure
    @author: lex.khuat
    """

    # ------ Public methods -------
    def getObj(self, classType, exclude=()):
        """
        Return list of instance by classType
        @param classType: type of returned class
        @param exclude: exclude items in return list
        @return: <List>Object
        """
        return list(item for item in self.__dict__.values()
                    if isinstance(item, classType)
                    and item not in exclude)

    def storeObj(self, name, obj, classType):
        """
        Add a class instance by classType
        @param name: instance name
        @param obj: object to add
        @param classType: type of returned class
        @return: self
        """
        if not isinstance(obj, classType):
            raise ValueError('%s must be %s classtype' % (obj, classType))
        for k, v in self.__dict__.items():
            if v is obj:
                if k is not name:
                    raise Exception('%s object already stored under another name: %s' % (obj, k))
                else:
                    return self
        self.__setattr__(name, obj)
        return self

    def destroy(self, object):
        """
        Destroy stored pages/engines/environment
        @param object: instance to destroy
        @return: self
        """
        name, val = None, None
        for k, v in self.__dict__.items():
            if v is object:
                name = k, val = v
                break
        if name not in (None, 'siteName'):
            delattr(self, val)
        return self
