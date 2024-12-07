import os
def get_conversations():
        walk_gen = os.walk("Conversations")
        walk_list = list(walk_gen)
        root = walk_list[0][0]
        files = [os.path.join(root, i) for i in walk_list[0][2]] or []
        return files

print('hellow'[25:])