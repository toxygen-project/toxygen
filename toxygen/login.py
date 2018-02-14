class Login:

    def __init__(self, arr):
        self.arr = arr

    def login_screen_close(self, t, number=-1, default=False, name=None):
        """ Function which processes data from login screen
        :param t: 0 - window was closed, 1 - new profile was created, 2 - profile loaded
        :param number: num of chosen profile in list (-1 by default)
        :param default: was or not chosen profile marked as default
        :param name: name of new profile
        """
        self.t = t
        self.num = number
        self.default = default
        self.name = name

    def get_data(self):
        return self.arr[self.num]