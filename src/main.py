"""
author: Marie-Neige Chapel
"""

import sys
from PyQt6 import QtWidgets
from main_window import MainWindow

# import json

# class A:
#     def __init__(self):
#         self.b_collection = []

# class B:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age


# class ABEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, A):
#             return {'A': obj.b_collection}
#         elif isinstance(obj, B):
#             return {'B': obj.__dict__}
#         return super().default(obj)


# a = A()
# a.b_collection.append(B("Tomer", "19"))
# a.b_collection.append(B("Bob", "21"))
# a.b_collection.append(B("Alice", "23"))
# print(json.dumps(a, cls=ABEncoder, indent=4))


app = QtWidgets.QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec())
