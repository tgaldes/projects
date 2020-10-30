from interface import Interface
# TODO: GMail service interface, thread interface

# ----------------- Interfaces -------------------
class IAction(Interface):
    def process(self, thread, matches):
        pass
class IMatcher(Interface):
    def matches(self, thread):
        pass
    def get_matching_groups(self, thread):
        pass

# ----------------- End Interfaces -------------------
