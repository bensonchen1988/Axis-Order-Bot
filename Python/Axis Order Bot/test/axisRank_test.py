import sys
sys.path.append("..")
import axisRank
import unittest

class RankTest(unittest.TestCase):

	def setUp(self):
		pass

	def test_get_rank(self):
		self.assertEqual(axisRank.get_rank(4), "Giant Toad")
		self.assertEqual(axisRank.get_rank(9), "Street Solicitor")
		self.assertEqual(axisRank.get_rank(14), "Soap Masseur/Masseuse")
		self.assertEqual(axisRank.get_rank(19), "Devout Follower")
		self.assertEqual(axisRank.get_rank(24), "Priest")
		self.assertEqual(axisRank.get_rank(29), "High Priest")
		self.assertEqual(axisRank.get_rank(34), "Megumin's Manatite")
		self.assertEqual(axisRank.get_rank(49), "Cecily's Panties")
		self.assertEqual(axisRank.get_rank(50), "Kazuma's Wallet")

	def test_next_threshold(self):
		self.assertEqual(axisRank.next_threshold("Giant Toad"), 5)
		self.assertEqual(axisRank.next_threshold("Street Solicitor"), 10)
		self.assertEqual(axisRank.next_threshold("Soap Masseur/Masseuse"), 15)
		self.assertEqual(axisRank.next_threshold("Devout Follower"), 20)
		self.assertEqual(axisRank.next_threshold("Priest"), 25)
		self.assertEqual(axisRank.next_threshold("High Priest"), 30)
		self.assertEqual(axisRank.next_threshold("Megumin's Manatite"), 35)
		self.assertEqual(axisRank.next_threshold("Cecily's Panties"), 50)
		self.assertEqual(axisRank.next_threshold("Kazuma's Wallet"), sys.maxsize)


if __name__ == '__main__':
	unittest.main()