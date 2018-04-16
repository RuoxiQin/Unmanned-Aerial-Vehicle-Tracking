#!/usr/bin/python
#-*-coding:utf-8-*-
class UCTTreeNode(object):
    '''The tree node of UCT search tree.'''
    def __init__(self,data, parent, untried_moves, action):
        self.data = data
        self.action = action
        self.untried_moves = untried_moves
        self.children = {}
        self.parent = parent
        return super(UCTTreeNode, self).__init__()
    def has_child(self):
        return self.children
    def has_parent(self):
        return self.parent
    def has_untried_moves(self):
        return self.untried_moves
    def get_path(self):
        '''Recursively get the path of this node.'''
        if self.has_parent():
            path = self.parent.get_path()
            path.append(self.action)
            return path
        else:
            return []
