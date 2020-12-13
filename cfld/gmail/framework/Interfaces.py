from interface import Interface
# TODO: GMail service interface, thread interface

class IAction(Interface):
    def process(self, thread, matches):
        pass
class IMatcher(Interface):
    def matches(self, thread):
        pass
    def get_matching_groups(self, thread):
        pass

class IRule(Interface):
    def process(self, thread):
        pass

class IOrg(Interface):
    def get_rule_construction_data(self):
        pass
    def get_imports(self):
        pass
