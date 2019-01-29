from LeafNode import LeafNode
from NonLeafNode import NonLeafNode
import numpy as np
import pandas as pd
import csv


class BPTree(object):
    def __init__(self, max_num_of_child):
        LeafNode.set_max_num_of_child(max_num_of_child)
        NonLeafNode.set_max_num_of_child(max_num_of_child)
        self.root = LeafNode(parent=None, kv_list=[], right_sibling=None)

    def insertion(self, node, entry):
        if not isinstance(node, LeafNode):
            result = node.add(entry)
            if result is not None:
                self.root = result
        else:
            kn_list = node.kn_list
            for n, N in enumerate(kn_list):
                if entry[0] < N[0]:
                    if n == 0:
                        node = node.left_node
                    break
                node = N[1]
            self.insertion(node, entry)

    def deletion(self, entry):
        target_node = self.root
        while not isinstance(target_node, LeafNode):
            kn_list = target_node.kn_list
            for n, N in enumerate(kn_list):
                if entry[0] < N[0]:
                    if n == 0:
                        target_node = target_node.left_node
                    break
                target_node = N[1]
        result = target_node.delete(entry)
        if result is not None:
            self.root = result
            self.root.parent = None

    def search(self, key):
        target_node = self.root
        while not isinstance(target_node, LeafNode):
            kn_list = target_node.kn_list
            for n, N in enumerate(kn_list):
                if key < N[0]:
                    if n == 0:
                        target_node = target_node.left_node
                    break
                target_node = N[1]
        k_list = list(np.array(target_node.kv_list)[:, 0])
        if key in k_list:
            key_index = k_list.index(key)
            return target_node.kv_list[key_index]
        else:
            return [key, 'N/A']


def insertion_deletion_test(max_num_of_child, input_file, delete_file):
    input_df = pd.read_table(input_file, header=None)
    input_list = list(zip(input_df[0].tolist(), input_df[1].tolist()))

    delete_df = pd.read_table(delete_file, header=None)
    delete_list = list(zip(delete_df[0].tolist(), delete_df[1].tolist()))

    input_result_title = input_file.split('/')[1].split('.')[0]
    delete_result_title = delete_file.split('/')[1].split('.')[0]
    print('max_num_of_child: ', max_num_of_child)
    bpt = BPTree(max_num_of_child)
    print("insertion start")
    print("0/10")
    for n, ent in enumerate(input_list):
        if (n + 1) % 100000 == 0:
            print(n // 100000 + 1, "/10")
        bpt.insertion(bpt.root, list(ent))
    print("insertion done")
    print()
    print("search start")
    print("0/10")
    with open('result/%s(%d).csv' % (input_result_title, max_num_of_child), 'w') as f:
        wr = csv.writer(f, delimiter='\t')
        for n, ent in enumerate(input_list):
            if (n + 1) % 100000 == 0:
                print(n // 100000 + 1, "/10")
            wr.writerow(bpt.search(list(ent)[0]))
    print("search done")
    print()
    print("deletion start")
    print("0/10")
    for n, ent in enumerate(delete_list):
        if (n + 1) % 100000 == 0:
            print(2*(n // 100000 + 1), "/10")
        bpt.deletion(list(ent))
    print("deletion done")
    print()
    print("search start")
    print("0/10")
    with open('result/%s(%d).csv' % (delete_result_title, max_num_of_child), 'w') as f:
        wr = csv.writer(f, delimiter='\t')
        for n, ent in enumerate(input_list):
            if (n + 1) % 100000 == 0:
                print(n // 100000 + 1, "/10")
            wr.writerow(bpt.search(list(ent)[0]))
    print("search done")


if __name__ == "__main__":

    test_list = [8, 12]
    for test_num in test_list:
        insertion_deletion_test(test_num, 'data/input.csv', 'data/delete.csv')

    test_list = [8, 12]
    for test_num in test_list:
        insertion_deletion_test(test_num, 'data/input2.csv', 'data/delete2.csv')



