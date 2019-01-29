from NonLeafNode import NonLeafNode
import numpy as np


class LeafNode(object):
    max_num_of_child = 0
    threshold = 0

    def __init__(self, parent=None, kv_list=[], right_sibling=None):
        self.num_of_child = len(kv_list)
        self.parent = parent
        self.kv_list = kv_list
        self.right_sibling = right_sibling

    @classmethod
    def set_max_num_of_child(cls, max_num_of_child):
        cls.max_num_of_child = max_num_of_child
        cls.threshold = (max_num_of_child - 1) // 2

    def add(self, entry):
        if self.num_of_child < self.max_num_of_child-1:
            self.add_entry_to_kv_list(entry)
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

    def add_entry_to_kv_list(self, entry):
        self.kv_list.append(entry)
        self.kv_list.sort(key=lambda x: x[0])
        self.num_of_child += 1

    def split(self, entry):
        k_list = list(np.array(self.kv_list)[:, 0])
        k_list.append(entry[0])
        k_list.sort()
        split_num = k_list[len(k_list) // 2]
        if split_num != entry[0]:
            k_list.remove(entry[0])
        index = k_list.index(split_num)  # split_num 이 삽입하려는 튜플일때 그 다음 key 기준으로 split, 아니면 그냥 split.

        new_node = LeafNode(parent=self.parent, kv_list=self.kv_list[index:], right_sibling=self.right_sibling)
        self.kv_list = self.kv_list[:index]
        self.num_of_child = len(self.kv_list)
        self.right_sibling = new_node
        if entry[0] == split_num:
            new_node.add_entry_to_kv_list(entry)
        else:
            if entry[0] < split_num:
                self.add_entry_to_kv_list(entry)
            else:
                new_node.add_entry_to_kv_list(entry)

        return [new_node.kv_list[0][0], new_node]

    def delete(self, entry):
        self.kv_list.remove(entry)

        if self.parent is None:
            if len(self.kv_list) >= 1:
                return None
            else:
                return LeafNode(parent=None, kv_list=[], right_sibling=None)
        else:
            if len(self.kv_list) >= self.threshold:
                if self.parent.left_node != self:
                    for n, kn in enumerate(self.parent.kn_list):
                        if kn[1] == self:
                            self.parent.kn_list[n][0] = self.kv_list[0][0]
                            break
                return None
            else:
                left_sibling = self.get_left_sibling()
                right_sibling = self.get_right_sibling()

                if left_sibling is None:
                    num_ls = 0
                else:
                    num_ls = len(left_sibling.kv_list)

                if right_sibling is None:
                    num_rs = 0
                else:
                    num_rs = len(right_sibling.kv_list)

                if num_rs >= num_ls:
                    if len(right_sibling.kv_list) > self.threshold+1:
                        self.borrow_from_right(right_sibling)
                        return None
                    else:
                        result = self.merge_with_right(right_sibling)
                        return result
                else:
                    if len(left_sibling.kv_list) > self.threshold+1:
                        self.borrow_from_left(left_sibling)
                        return None
                    else:
                        result = self.merge_with_left(left_sibling)
                        return result

    def borrow_from_right(self, node):
        self.add_entry_to_kv_list(node.kv_list[0])
        node.kv_list = node.kv_list[1:]
        for n, kn in enumerate(node.parent.kn_list):
            if kn[1] == node:
                node.parent.kn_list[n][0] = node.kv_list[0][0]
                break

    def borrow_from_left(self, node):
        self.add_entry_to_kv_list(node.kv_list[-1])
        node.kv_list = node.kv_list[:-1]
        for n, kn in enumerate(self.parent.kn_list):
            if kn[1] == self:
                self.parent.kn_list[n][0] = self.kv_list[0][0]
                break

    def merge_with_right(self, node):
        self.kv_list = self.kv_list + node.kv_list
        self.right_sibling = node.right_sibling
        result = self.parent.delete(node)
        return result

    def merge_with_left(self, node):
        node.kv_list = node.kv_list + self.kv_list
        node.right_sibling = self.right_sibling
        result = node.parent.delete(self)
        return result

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


