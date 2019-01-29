import numpy as np


class NonLeafNode(object):
    max_num_of_child = 0
    threshold = 0

    def __init__(self, parent=None, kn_list=[], left_node=None):
        self.num_of_child = len(kn_list)
        self.parent = parent
        self.kn_list = kn_list
        self.left_node = left_node

    @classmethod
    def set_max_num_of_child(cls, max_num_of_child):
        cls.max_num_of_child = max_num_of_child
        cls.threshold = (max_num_of_child-1)//2

    def add(self, entry):
        if self.num_of_child < self.max_num_of_child-1:
            self.add_entry_to_kn_list(entry)
            return None
        else:
            new_kn = self.split(entry)
            if self.parent is None:  # parent 가 없으면 새 노드를 생성
                new_node = NonLeafNode(parent=None, kn_list=[new_kn], left_node=self)
                self.parent = new_node
                new_kn[1].parent = new_node
                return new_node
            else:  # parent 가 있으면, kn쌍 하나 만들어서 parent 노드에 add
                result = self.parent.add(new_kn)
                return result

    def add_entry_to_kn_list(self, entry):
        self.kn_list.append(entry)
        self.kn_list.sort(key=lambda x: x[0])
        self.num_of_child += 1

    def split(self, entry):
        #  만약 split이 root에서 일어난다면, return 되는 튜플을 root로 설정한다.
        k_list = list(np.array(self.kn_list)[:, 0])
        k_list.append(entry[0])
        k_list.sort()
        split_num = k_list[len(k_list) // 2]

        if split_num != entry[0]:
            k_list.remove(entry[0])
        index = k_list.index(split_num)

        _key = self.kn_list[index][0]
        if split_num == entry[0]:
            new_right_node = NonLeafNode(parent=self.parent, kn_list=self.kn_list[index:], left_node=entry[1])
            self.kn_list = self.kn_list[:index]
            _key = entry[0]
        else:
            new_right_node = NonLeafNode(parent=self.parent, kn_list=self.kn_list[index+1:],
                                         left_node=self.kn_list[index][1])
            self.kn_list = self.kn_list[:index]
            if entry[0] < split_num:
                self.add_entry_to_kn_list(entry)
            else:
                new_right_node.add_entry_to_kn_list(entry)

        self.num_of_child = len(self.kn_list)
        new_kn_list = new_right_node.kn_list
        for node in new_kn_list:
            node[1].parent = new_right_node
        new_right_node.left_node.parent = new_right_node
        return [_key, new_right_node]

    def delete(self, node_link):

        if self.left_node == node_link:
            self.left_node = self.kn_list[0][1]
            self.kn_list = self.kn_list[1:]
        else:
            for n, kn in enumerate(self.kn_list):
                if kn[1] == node_link:
                    self.kn_list.remove(kn)
                    break

        if len(self.kn_list) >= self.threshold:
            return None
        else:
            if self.parent is None:
                if len(self.kn_list) >= 1:
                    return None
                else:
                    self.left_node.parent = None
                    return self.left_node
            else:
                left_sibling = self.get_left_sibling()
                right_sibling = self.get_right_sibling()

                if left_sibling is None:
                    num_ls = 0
                else:
                    num_ls = len(left_sibling.kn_list)

                if right_sibling is None:
                    num_rs = 0
                else:
                    num_rs = len(right_sibling.kn_list)

                if num_rs >= num_ls:
                    if len(right_sibling.kn_list) > self.threshold:
                        self.borrow_from_right(right_sibling)
                        return None
                    else:
                        result = self.merge_with_right(right_sibling)
                        return result
                else:
                    if len(left_sibling.kn_list) > self.threshold:
                        self.borrow_from_left(left_sibling)
                        return None
                    else:
                        result = self.merge_with_left(left_sibling)
                        return result

    def borrow_from_right(self, node):
        _index = 0
        if self.parent.left_node == self:
            _key = self.parent.kn_list[0][0]
        else:
            for n, kn in enumerate(self.parent.kn_list):
                if kn[1] == self:
                    _index = n+1
                    _key = self.parent.kn_list[_index][0]
                    break
        self.add_entry_to_kn_list([_key, node.left_node])
        node.left_node.parent = self
        self.parent.kn_list[_index][0] = node.kn_list[0][0]
        node.left_node = node.kn_list[0][1]
        node.kn_list = node.kn_list[1:]

    def borrow_from_left(self, node):
        for n, kn in enumerate(self.parent.kn_list):
            if kn[1] == self:
                _index = n
                _key = self.parent.kn_list[_index][0]
                break
        self.add_entry_to_kn_list([_key, self.left_node])
        self.parent.kn_list[_index][0] = node.kn_list[-1][0]
        self.left_node = node.kn_list[-1][1]
        self.left_node.parent = self
        node.kn_list = node.kn_list[:-1]

    def merge_with_right(self, node):
        to_leaf_node = node.left_node
        while to_leaf_node.__class__.__name__ != "BPLeafNode":
            to_leaf_node = to_leaf_node.left_node
        _key = to_leaf_node.kv_list[0][0]

        self.add_entry_to_kn_list([_key, node.left_node])
        self.kn_list = self.kn_list + node.kn_list
        node.left_node.parent = self
        for kn in node.kn_list:
            kn[1].parent = self
        return self.parent.delete(node)

    def merge_with_left(self, node):
        to_leaf_node = self.left_node
        while to_leaf_node.__class__.__name__ != "BPLeafNode":
            to_leaf_node = to_leaf_node.left_node
        _key = to_leaf_node.kv_list[0][0]
        node.add_entry_to_kn_list([_key, self.left_node])
        self.left_node.parent = node
        node.kn_list = node.kn_list + self.kn_list
        for kn in self.kn_list:
            kn[1].parent = node
        return node.parent.delete(self)

    def get_right_sibling(self):
        if self.parent.left_node == self:
            return self.parent.kn_list[0][1]
        elif self.parent.kn_list[-1][1] == self:
            return None
        elif self.parent.kn_list[0][1] == self:
            return self.parent.kn_list[1][1]
        else:
            for n, kn in enumerate(self.parent.kn_list):
                if kn[1] == self:
                    return self.parent.kn_list[n+1][1]

    def get_left_sibling(self):
        if self.parent.left_node == self:
            return None
        elif self.parent.kn_list[0][1] == self:
            return self.parent.left_node
        else:
            for n, kn in enumerate(self.parent.kn_list):
                if kn[1] == self:
                    return self.parent.kn_list[n-1][1]