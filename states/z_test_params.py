# import unittest
#
# from params import Params
#
#
# class TestParamGet(unittest.TestCase):
#
#     def test_get(self):
#         print(Params.tolerance())
#
#
# class TestParamSet(unittest.TestCase):
#     def setUp(self):
#         self.og_value = Params.tolerance()
#
#     def tearDown(self):
#         print(Params.tolerance())
#         Params.hard_reset()
#         # Params.tolerance(self.og_value)
#         # print('reverted to: ', Params.tolerance())
#
#     def test_set(self):
#         Params.tolerance(15)
#         print('new tolerance: ', Params.tolerance())
#
#
# if __name__ == '__main__':
#     unittest.main()
