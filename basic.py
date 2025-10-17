class basic_similation_element:
    def __init__(self):
        print("object init:",type(self).__name__)
    def __del__(self):
        print("object destroy:",type(self).__name__)
