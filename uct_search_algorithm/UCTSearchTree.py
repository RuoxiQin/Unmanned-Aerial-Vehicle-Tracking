#!/usr/bin/python
#-*-coding:utf-8-*-
class UCTSearchTree(object):
    def __init__(self, data, untried_moves):
        self.root = UCTTreeNode(data, None, untried_moves, None)
        return super(UCTSearchTree, self).__init__()

    def get_node(self, path_raw):
        '''This function return the node based on the given path.'''
        path = path_raw[:]
        return self._get_node(path, self.root) #use the _get_node recursvly

    def _get_node(self, path, node):
        '''This is the recursive part of get_node function'''
        if node.has_child() and path:
            #need to reach next child node
            action = path.pop(0)
            assert action in node.children.keys()
            return self._get_node(path, node.children[action])
        else:
            #get the end of the path
            return node

    def has_node(self, path_raw):
        '''this function return whether there is a node in the end of the path.'''
        path = path_raw[:]
        return self._has_node(path, self.root) #use the _get_node recursivly

    def _has_node(self, path, node):
        '''This is the recursive part of has_node function'''
        if node.has_child() and path:
            #need to reach next child node
            action = path.pop(0)
            assert action in node.children.keys()
            return self._has_node(path, node.children[action])
        elif not path:
            #search down the whole path and there are still child nodes
            return True
        else:
            #reach the end of the path
            return False

    def find_optimized(self, choose_priority_calc_func):
        '''This function return the optimized leaf node.'''
        return self._find_optimized(self.root, choose_priority_calc_func)

    def _find_optimized(self, node, choose_priority_calc_func):
        '''Recursively find the optimized leaf node.'''
        if node.has_untried_moves():
            path = node.get_path()
            assert node.has_untried_moves()
            path.append(random.choice(node.untried_moves))
            return path
        elif node.has_child():
            children_nodes = []
            for child_action in node.children.keys():
                children_nodes.append(node.children[child_action])
            return self._find_optimized((sorted(children_nodes, key=choose_priority_calc_func))[-1], choose_priority_calc_func)
        else:
            return node.get_path()

    def add_children(self, path, data, untried_moves):
        '''This method add the new node as a child of parent and return it. If the child already existed, it would not add it'''
        assert len(path) != 0
        action = path.pop()
        parent = self.get_node(path)
        if not parent.children.has_key(action):  
            assert action in parent.untried_moves
            parent.untried_moves.remove(action)
            parent.children[action] = UCTTreeNode(data, parent, untried_moves, action)
        return parent.children[action]



    def refresh_tree(self, path, refresh_rule_func):
        '''This function refresh the whole tree from the bottom node to the root.'''
        node = self.get_node(path)
        self._refresh_tree(node, refresh_rule_func)

    def _refresh_tree(self, node, refresh_rule_func):
        '''This function refresh the tree recursivly.'''
        node.data = refresh_rule_func(node.data)
        if node.has_parent():
            node = node.parent
            self._refresh_tree(node, refresh_rule_func)  
