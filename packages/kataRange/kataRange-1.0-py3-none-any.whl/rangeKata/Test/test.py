import unittest
from kataRange import rango

class testCases(unittest.TestCase):
    def test_Contains(self):
        rango1 = rango("[2,6)")
        self.assertEqual(rango1.contains([2,4]),True)
        self.assertEqual(rango1.contains([-1,1,6,10]),False)    
    def test_getAll(self):
        rango1 = rango("[2,6)")
        self.assertEqual(rango1.getAllPoints(), [2,3,4,5])
    def test_Equals(self):
        rango1 = rango("[3,5)")
        rango2 = rango("[2,10)")
        rango3 = rango("[2,5)")
        rango4 = rango("[3,10)")
        rango5 = rango("[2,10)")
        self.assertEqual(rango1.equals(rango1),True)
        self.assertEqual(rango2.equals(rango1),False)
        self.assertEqual(rango3.equals(rango4),False)
        self.assertEqual(rango1.equals(rango5),False)

    def test_endPoints(self):
        rango1 = rango("[2,6)") 
        rango2 = rango("[2,6]")        
        rango3 = rango("(2,6)")        
        rango4 = rango("(2,6]")        

        self.assertEqual(rango1.endpoints(), (2,5))
        self.assertEqual(rango2.endpoints(), (2,6))
        self.assertEqual(rango3.endpoints(), (3,5))
        self.assertEqual(rango4.endpoints(), (3,6))

    def test_containsRange(self):
        rango1 = rango("[2,5)")
        rango2 = rango("[7,10)")
        rango3 = rango("[3,10)")
        rango4 = rango("[3,5)")
        rango5 = rango("[2,10)")
        rango6 = rango("[3,5]")

        self.assertEqual(rango1.containsRange(rango2), False)
        self.assertEqual(rango1.containsRange(rango3), False)
        self.assertEqual(rango4.containsRange(rango5), False)
        self.assertEqual(rango5.containsRange(rango6), True)
        self.assertEqual(rango6.containsRange(rango6), True)

    def test_overlapsRange(self):
        rango1 = rango("[2,5)")
        rango2 = rango("[7,10)")
        rango3 = rango("[3,10)")
        rango4 = rango("[3,5)")
        rango5 = rango("[2,10)")
        self.assertEqual(rango1.overlapsRange(rango2), False)
        self.assertEqual(rango5.overlapsRange(rango4), True)
        self.assertEqual(rango4.overlapsRange(rango4), True)
        self.assertEqual(rango1.overlapsRange(rango3), True)
        self.assertEqual(rango4.overlapsRange(rango5), True)
